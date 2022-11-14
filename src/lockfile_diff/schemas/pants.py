from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import IO, ClassVar

from lockfile_diff.base import Format, InputSchema, Schema
from lockfile_diff.formats.blocks import CommentBlock, Sections
from lockfile_diff.types import LockfileInfo, ParsedData


@dataclass(frozen=True)
class PantsLockfileData(ParsedData):
    embedded: ParsedData

    def get_info(self) -> LockfileInfo:
        return self.embedded.get_info()


class PantsLockfileSchema(InputSchema):
    headerlines_prefix: ClassVar[str]

    @abstractmethod
    def parse_embedded(self, source: IO) -> ParsedData:
        raise NotImplementedError()

    def parse(self, source: IO) -> ParsedData:
        header = CommentBlock(prefix=self.headerlines_prefix).parse(source)
        metadata = Sections(delimiter="^--- ", keep=1).parse(header.source)
        return PantsLockfileData(
            raw=Format("json").parse(metadata.source).raw,
            embedded=self.parse_embedded(source),
        )


class PantsPexLockfileSchema(PantsLockfileSchema):
    schema = "pants-pex"
    headerlines_prefix = "//"

    def parse_embedded(self, source: IO) -> ParsedData:
        return Schema("pex").parse(source)


class PantsCoursierLockfileSchema(PantsLockfileSchema):
    schema = "pants-coursier"
    headerlines_prefix = "#"

    def parse_embedded(self, source: IO) -> ParsedData:
        return Schema("coursier").parse(source)
