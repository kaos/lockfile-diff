from __future__ import annotations

from typing import IO, Any, Iterator, Mapping, overload

from click import style

from lockfile_diff.base import OutputFormat
from lockfile_diff.types import LockfileDiff, ParsedVersion


class Text(OutputFormat):
    format = "text"

    BUMPS = (
        ("major", "==", "red"),
        ("minor", "--", "bright_red"),
        ("micro", "  ", "bright_yellow"),
    )

    @overload
    def encode(self, data: Any, dest: IO) -> None:
        ...

    @overload
    def encode(self, data: Any) -> str:
        ...

    def encode(self, data: Any, dest: IO | None = None) -> None | str:
        if isinstance(data, LockfileDiff):
            output = "\n".join(self.print_diff(data))
        else:
            raise ValueError(f"Unexpected data to encode: {data!r}")
        if dest is None:
            return output
        else:
            dest.write(output)
        return None

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
        cls, title: str, reqs: Mapping[str, tuple[ParsedVersion, ParsedVersion]]
    ) -> Iterator[str]:
        if not reqs:
            return

        yield cls.title(title)
        for name, (prev, curr) in reqs.items():
            name_s = style(f"{name:30}", fg="yellow")
            prev_s = style(f"{str(prev):10}", fg="cyan")
            curr_s = style(f"{curr}", fg="green")
            bump_s = cls.get_bump_s(prev, curr)
            yield f"  {name_s} {prev_s} {bump_s} {curr_s}"

    @classmethod
    def print_reqs(cls, heading: str, reqs: Mapping[str, ParsedVersion], **kwargs) -> Iterator[str]:
        if not reqs:
            return

        yield cls.title(heading)
        for name, version in reqs.items():
            yield style(f"  {name:30} {version}", **kwargs)

    @classmethod
    def get_bump_s(cls, prev: ParsedVersion, curr: ParsedVersion) -> str:
        attrs: dict[str, Any] = {}
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
