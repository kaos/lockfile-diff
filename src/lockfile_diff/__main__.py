#!/usr/bin/env python
from __future__ import annotations

import sys
from io import StringIO
from subprocess import CalledProcessError, run
from textwrap import dedent
from typing import IO

import click

from lockfile_diff import formats, schemas  # noqa
from lockfile_diff.base import Format
from lockfile_diff.errors import FAILED_TO_OPEN_FILE
from lockfile_diff.parser import Parser
from lockfile_diff.registries import Registries


@click.command
@click.option("--old-lockfile", "--old", metavar="LOCKFILE", type=click.File())
@click.option("--new-lockfile", "--new", metavar="LOCKFILE", type=click.File())
@click.option(
    "--lockfile-schema",
    type=click.Choice(tuple(Registries.get_default().schemas.keys())),
    default="auto-detect",
    help="Parse LOCKFILEs using SCHEMA",
)
@click.option(
    "--compare",
    metavar="COMMIT",
    help=dedent(
        """Git commit sha, tag or branch. See gitrevisions(7) for acceptable values. Use in place of
        either the --old-lockfile or the --new-lockfile, to get the file contents from that git
        revision to compare with.
        """
    ),
)
@click.option(
    "--output-format",
    type=click.Choice(tuple(Registries.get_default().output_formats.keys())),
    default="text",
    help="Print resulting diff using OUTPUT_FORMAT.",
)
@click.option("--unchanged/--no-unchanged", default=False)
@click.option("--changed/--no-changed", default=True)
@click.option("--added/--no-added", default=True)
@click.option("--removed/--no-removed", default=True)
@click.option(
    "--no-fail",
    is_flag=True,
    default=False,
    help="Treat missing input file as empty. Silence error message from `auto-detect` SCHEMA.",
)
def main(
    lockfile_schema,
    output_format,
    old_lockfile,
    new_lockfile,
    compare,
    unchanged,
    changed,
    added,
    removed,
    no_fail,
):
    if old_lockfile is None and compare:
        assert new_lockfile is not None, "Must provide either --old or --new lockfile"
        old_lockfile = get_git_file(new_lockfile.name, compare, quiet=no_fail)
    if new_lockfile is None:
        assert old_lockfile is not None, "Must provide either --old or --new lockfile"
        new_lockfile = get_git_file(old_lockfile.name, compare, quiet=no_fail)
    if not no_fail and (old_lockfile is None or new_lockfile is None):
        sys.exit(FAILED_TO_OPEN_FILE)

    kwargs = {}
    if lockfile_schema == "auto-detect" and no_fail:
        kwargs["quiet"] = True

    diff = Parser.diff(old_lockfile, new_lockfile, lockfile_schema, **kwargs)

    if not unchanged:
        diff.unchanged.clear()
    if not changed:
        diff.upgraded.clear()
        diff.downgraded.clear()
    if not added:
        diff.added.clear()
    if not removed:
        diff.removed.clear()

    click.echo(Format(output_format).encode(diff))
    return 0


class NamedStringIO(StringIO):
    def __init__(self, *args, name: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name


def get_git_file(filename: str, commit: str, quiet: bool) -> IO | None:
    try:
        file_contents = run(
            ["git", "show", f"{commit}:{filename}"], check=True, capture_output=True, text=True
        ).stdout
        return NamedStringIO(
            file_contents,
            name=f"[git: {commit}] {filename}",
        )
    except CalledProcessError as e:
        if not quiet:
            click.echo(f"ERROR: {e}", err=True)
        return None


if __name__ == "__main__":
    main()
