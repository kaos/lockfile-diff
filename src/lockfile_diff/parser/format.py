from __future__ import annotations

import json
import re
from io import StringIO
from itertools import count
from typing import IO, Any

from lockfile_diff.util.class_registry.decorator import class_registry
from lockfile_diff.util.class_registry.meta import get_implementation, get_trait_implementations


@class_registry(format="format")
class Format:
    @classmethod
    def parse(cls, content: IO, format: str) -> Any:
        return get_implementation(cls, format=format).parse(content)

    @classmethod
    def chain(cls, kwargs: dict | None = None, **selection) -> FormatChain:
        return FormatChain(cls, get_implementation(cls, **selection), kwargs or {})


class FormatChain:
    def __init__(
        self,
        format: type[Format],
        impl: type[Format],
        kwargs: dict,
        parent: FormatChain | None = None,
    ):
        self.format = format
        self.impl = impl
        self.kwargs = kwargs
        self.parent = parent

    def parse(self, content: IO) -> Any:
        if self.parent:
            content = self.parent.parse(content)
        return self.impl.parse(content, **self.kwargs)

    def chain(self, kwargs: dict | None = None, **selection) -> FormatChain:
        return FormatChain(
            self.format, get_implementation(self.format, **selection), kwargs or {}, self
        )


class AutoDetect(Format):
    format = "auto-detect"

    @classmethod
    def parse(cls, content: IO) -> Any:
        for impl in get_trait_implementations(cls, "format"):
            if impl is AutoDetect:
                continue
            try:
                res = impl.parse(content)
                return res
            except Exception:
                content.seek(0)

        raise ValueError(f"{content}: failed to auto detect lock file format")


class JSON(Format):
    @classmethod
    def parse(cls, content: IO) -> Any:
        return json.load(content)


class CommentBlock(Format):
    @classmethod
    def parse(cls, content: IO, comment_prefix: str = "//") -> Any:
        longest_common_prefix: str | None = None
        lines = content.readlines()
        for line in lines:
            if not line.startswith(comment_prefix):
                longest_common_prefix = None
                break
            if longest_common_prefix is None:
                longest_common_prefix = line
                continue
            for left, right, c in zip(longest_common_prefix, line, count()):
                if right in (left, "\n"):
                    continue
                longest_common_prefix = longest_common_prefix[:c]
                break
        if not longest_common_prefix:
            raise ValueError("not a comment block")

        # Compile prefix regexp prefix substitution pattern, trailing spaces is optional.
        prefix = re.compile("^" + re.escape(longest_common_prefix).replace(" ", " ?"))
        res = StringIO()
        res.writelines(prefix.sub("", line) for line in lines)
        res.seek(0)
        return res


class Sections(Format):
    @classmethod
    def parse(
        cls, content: IO, section_delimiter: str = "^\n$", select_section: int | None = None
    ) -> Any:
        sections = []
        lines = []
        while line := content.readline():
            if re.search(section_delimiter, line):
                sections.append(StringIO("".join(lines)))
                lines.clear()
            else:
                lines.append(line)

        if lines:
            sections.append(StringIO("".join(lines)))

        if select_section is None:
            return sections

        return sections[select_section]
