from __future__ import annotations

import json
from dataclasses import asdict
from typing import Iterator, Mapping

import yaml
from click import style
from packaging.version import Version

from lockfile_diff.info import LockfileDiff
from lockfile_diff.util.class_registry.decorator import class_registry
from lockfile_diff.util.class_registry.meta import get_implementation


@class_registry(format="format")
class Encoder:
    @classmethod
    def encode(cls, diff: LockfileDiff, format: str) -> str:
        return get_implementation(cls, format=format).encode(diff)


class Text(Encoder):
    format = "text"

    BUMPS = (
        ("major", "==", "red"),
        ("minor", "--", "bright_red"),
        ("micro", "  ", "bright_yellow"),
    )

    @classmethod
    def encode(cls, diff: LockfileDiff) -> str:
        return "\n".join(cls.print_diff(diff))

    @classmethod
    def print_diff(cls, diff: LockfileDiff) -> Iterator[str]:
        yield from cls.print_reqs("Unchanged dependencies", diff.unchanged, fg="blue")
        yield from cls.print_changed("Upgraded dependencies", diff.upgraded)
        yield from cls.print_changed("Downgraded dependencies", diff.downgraded)
        yield from cls.print_reqs("Added dependencies", diff.added, fg="bright_green")
        yield from cls.print_reqs("Removed dependencies", diff.removed, fg="magenta")
        yield ""

    @classmethod
    def title(cls, text: str) -> str:
        heading = f"== {text:^60} =="
        return style("\n".join((" " * len(heading), heading, "")), underline=True)

    @classmethod
    def print_changed(
        cls, title: str, reqs: Mapping[str, tuple[Version, Version]]
    ) -> Iterator[str]:
        if not reqs:
            return

        yield cls.title(title)
        for name, (prev, curr) in reqs.items():
            name_s = style(f"{name:30}", fg="yellow")
            prev_s = style(f"{str(prev):8}", fg="cyan")
            curr_s = style(f"{curr}", fg="green")
            bump_s = cls.get_bump_s(prev, curr)
            yield f"  {name_s} {prev_s} {bump_s} {curr_s}"

    @classmethod
    def print_reqs(cls, heading: str, reqs: Mapping[str, Version], **kwargs) -> Iterator[str]:
        if not reqs:
            return

        yield cls.title(heading)
        for name, version in reqs.items():
            yield style(f"  {name:30} {version}", **kwargs)

    @classmethod
    def get_bump_s(cls, prev: Version, curr: Version) -> str:
        attrs = {}
        for key, label, fg in cls.BUMPS:
            if getattr(prev, key) == getattr(curr, key):
                continue
            attrs["fg"] = fg
            if prev > curr:
                label = f"<{label}"
                attrs["blink"] = True
            else:
                label += ">"
            break
        else:
            label = "???"
            attrs["fg"] = "magenta"
        return style(f"{label:^7}", **attrs)


class JSON(Encoder):
    format = "json"

    @classmethod
    def encode(cls, diff: LockfileDiff) -> str:
        return json.dumps(asdict(diff), cls=JSONEncoder)


class YAML(Encoder):
    format = "yaml"

    @classmethod
    def encode(cls, diff: LockfileDiff) -> str:
        return yaml.safe_dump(asdict(diff))


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Version):
            return str(o)
        return super().default(o)


def yaml_represent_version(dumper, data):
    return dumper.represent_str(str(data))


yaml.add_representer(Version, yaml_represent_version, Dumper=yaml.SafeDumper)
