#!/usr/bin/env python
from __future__ import annotations

import itertools
import json
from io import StringIO
from subprocess import run
from textwrap import dedent
from typing import IO, Any, Mapping

import click


@click.command
@click.option("--old-lockfile", "--old", metavar="LOCKFILE", type=click.File())
@click.option("--new-lockfile", "--new", metavar="LOCKFILE", type=click.File())
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
@click.option("--unchanged/--no-unchanged", default=False)
@click.option("--changed/--no-changed", default=True)
@click.option("--added/--no-added", default=True)
@click.option("--removed/--no-removed", default=True)
def main(old_lockfile, new_lockfile, compare, unchanged, changed, added, removed):
    if old_lockfile is None and compare:
        assert new_lockfile is not None, "Must provide either --old or --new lockfile"
        old_lockfile = get_git_file(new_lockfile.name, compare)
    if new_lockfile is None:
        assert old_lockfile is not None, "Must provide either --old or --new lockfile"
        new_lockfile = get_git_file(old_lockfile.name, compare)
    old, new = (read_lockfile(lockfile) for lockfile in (old_lockfile, new_lockfile))
    old_reqs, new_reqs = (locked_requirements(lockfile) for lockfile in (old, new))
    diff = {
        name: (old_reqs.get(name), new_reqs.get(name))
        for name in sorted({*old_reqs.keys(), *new_reqs.keys()})
        if old_reqs.get(name) != new_reqs.get(name)
    }

    if unchanged:
        print_reqs(
            "Unchanged dependencies",
            {name: version for name, version in new_reqs.items() if name not in diff},
            fg="blue",
        )

    if changed:
        print_changed(diff)

    if added:
        print_reqs(
            "Added dependencies",
            {name: version for name, version in new_reqs.items() if name not in old_reqs},
            fg="bright_green",
        )

    if removed:
        print_reqs(
            "Removed dependencies",
            {name: version for name, version in old_reqs.items() if name not in new_reqs},
            fg="magenta",
        )

    click.echo()


def print_changed(reqs: Mapping[str, tuple[str, str]]) -> None:
    if not reqs:
        return

    title("Changed dependencies")
    for name, (prev, curr) in reqs.items():
        if prev is None or curr is None:
            continue
        name_s = click.style(f"{name:30}", fg="yellow")
        prev_s = click.style(f"{prev:8}", fg="cyan")
        curr_s = click.style(f"{curr}", fg="green")
        bump_s = get_bump_s(prev, curr)
        click.echo(f"  {name_s} {prev_s} {bump_s} {curr_s}")


def print_reqs(heading: str, reqs: Mapping[str, str], **kwargs) -> None:
    if not reqs:
        return

    title(heading)
    for name, version in reqs.items():
        click.secho(f"  {name:30} {version}", **kwargs)


def title(text: str) -> None:
    heading = f"== {text:^60} =="
    click.secho("\n".join((" " * len(heading), heading, "")), underline=True)


BUMPS = (
    ("==", "red"),
    ("--", "bright_red"),
    ("  ", "bright_yellow"),
    ("??", "magenta"),
)


def get_bump_s(prev: str, curr: str) -> str:
    attrs = {}
    for p, c, bump in zip(prev.split("."), curr.split("."), BUMPS):
        if p == c:
            continue
        label, attrs["fg"] = bump
        try:
            if int(p) > int(c):
                label = f"<{label}"
                attrs["blink"] = True
            else:
                label += ">"
        except ValueError:
            label += label[0]
        break
    else:
        label, attrs["fg"] = BUMPS[-1]
        label += "?"

    return click.style(f"{label:^7}", **attrs)


def get_git_file(filename: str, commit: str) -> IO:
    return StringIO(
        run(
            ["git", "show", f"{commit}:{filename}"], check=True, capture_output=True, text=True
        ).stdout
    )


def read_lockfile(fd, comment_prefix: str = "//") -> Mapping[str, Any]:
    if not fd:
        return {}
    while line := fd.readline():
        if line.startswith(comment_prefix):
            continue
        break
    return json.load(fd)


def locked_requirements(lockfile: Mapping[str, Any]) -> Mapping[str, str]:
    all_locked_requirements = (
        resolve.get("locked_requirements", []) for resolve in lockfile.get("locked_resolves", [])
    )
    return {
        locked["project_name"]: locked["version"]
        for locked in itertools.chain.from_iterable(all_locked_requirements)
    }


if __name__ == "__main__":
    main()
