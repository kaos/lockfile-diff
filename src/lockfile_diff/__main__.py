#!/usr/bin/env python
from __future__ import annotations

from io import StringIO
from subprocess import run
from textwrap import dedent
from typing import IO

import click

from lockfile_diff.core import DataRegistry
from lockfile_diff.output import Encoder, Text
from lockfile_diff.parser import pants  # noqa
from lockfile_diff.parser.format import AutoDetect, Format
from lockfile_diff.util.class_registry.option import class_registry_option


@click.command
@click.option("--old-lockfile", "--old", metavar="LOCKFILE", type=click.File())
@click.option("--new-lockfile", "--new", metavar="LOCKFILE", type=click.File())
@class_registry_option(
    Format,
    "--input-format",
    trait="format",
    default=AutoDetect.format,
    help="Parse LOCKFILE using FORMAT",
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
@class_registry_option(
    Encoder,
    "--output-format",
    trait="format",
    default=Text.format,
    help="Print resulting diff using OUTPUT_FORMAT.",
)
@click.option("--unchanged/--no-unchanged", default=False)
@click.option("--changed/--no-changed", default=True)
@click.option("--added/--no-added", default=True)
@click.option("--removed/--no-removed", default=True)
def main(
    input_format,
    output_format,
    old_lockfile,
    new_lockfile,
    compare,
    unchanged,
    changed,
    added,
    removed,
):
    if old_lockfile is None and compare:
        assert new_lockfile is not None, "Must provide either --old or --new lockfile"
        old_lockfile = get_git_file(new_lockfile.name, compare)
    if new_lockfile is None:
        assert old_lockfile is not None, "Must provide either --old or --new lockfile"
        new_lockfile = get_git_file(old_lockfile.name, compare)

    old_data, new_data = (
        Format.parse(lockfile, input_format) for lockfile in (old_lockfile, new_lockfile)
    )
    old_info, new_info = (DataRegistry.get_info(data) for data in (old_data, new_data))
    diff = new_info.diff(old_info)

    if not unchanged:
        diff.unchanged.clear()
    if not changed:
        diff.upgraded.clear()
        diff.downgraded.clear()
    if not added:
        diff.added.clear()
    if not removed:
        diff.removed.clear()

    click.echo(Encoder.encode(diff, output_format))
    return 0


def get_git_file(filename: str, commit: str) -> IO:
    return StringIO(
        run(
            ["git", "show", f"{commit}:{filename}"], check=True, capture_output=True, text=True
        ).stdout
    )


if __name__ == "__main__":
    main()
