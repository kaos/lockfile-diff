from __future__ import annotations

import re
from dataclasses import dataclass
from io import StringIO
from itertools import count
from typing import IO, Any, Sequence

from lockfile_diff.base import InputBase
from lockfile_diff.types import ParsedData
from lockfile_diff.util.io.rewind import capture


class ParsedCommentBlock(ParsedData):
    @classmethod
    def create(cls, comment_block: str) -> ParsedCommentBlock:
        return cls(raw=dict(comment_block=comment_block))

    @property
    def source(self) -> IO:
        return StringIO(self.raw["comment_block"])


@dataclass(frozen=True)
class CommentBlock(InputBase):
    prefix: str

    def parse(self, source: IO) -> ParsedData:
        longest_common_prefix: str | None = None
        lines: list[str] = []
        with capture(source) as c:
            while line := source.readline():
                if not line.strip():
                    c.commit()
                    continue
                if not line.startswith(self.prefix):
                    break
                lines.append(line)
                c.commit()
                if longest_common_prefix is None:
                    longest_common_prefix = line
                    continue
                for left, right, idx in zip(longest_common_prefix, line, count()):
                    if right in (left, "\n"):
                        continue
                    longest_common_prefix = longest_common_prefix[:idx]
                    break
        if not longest_common_prefix:
            raise ValueError("not a comment block")

        # Compile prefix regexp prefix substitution pattern, trailing spaces is optional.
        prefix = re.compile("^" + re.escape(longest_common_prefix).replace(" ", " ?"))
        return ParsedCommentBlock.create("".join(prefix.sub("", line) for line in lines))

    def encode(self, dest: IO, data: Any) -> None:
        raise NotImplementedError()


class ParsedSections(ParsedData):
    @classmethod
    def create(cls, sections: Sequence[str]) -> ParsedSections:
        return cls(raw=dict(sections=sections))

    @property
    def source(self) -> IO:
        return StringIO("\n".join(self.raw["sections"]))


@dataclass(frozen=True)
class Sections(InputBase):
    delimiter: str
    keep: slice | int

    def parse(self, source: IO) -> ParsedData:
        sections = []
        lines: list[str] = []
        while line := source.readline():
            if re.search(self.delimiter, line):
                sections.append("".join(lines))
                lines.clear()
            else:
                lines.append(line)

        if lines:
            sections.append("".join(lines))

        s = self.keep if isinstance(self.keep, slice) else slice(self.keep, self.keep + 1)
        return ParsedSections.create(tuple(sections[s]))

    def encode(self, dest: IO, data: Any) -> None:
        raise NotImplementedError()
