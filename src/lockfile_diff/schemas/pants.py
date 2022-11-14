from __future__ import annotations

from dataclasses import dataclass
from typing import IO, cast

from lockfile_diff.base import Format, InputSchema, Schema
from lockfile_diff.formats.blocks import CommentBlock, Sections
from lockfile_diff.schemas.pex import PexLockfileData
from lockfile_diff.types import LockfileInfo, ParsedData


@dataclass(frozen=True)
class PantsPexLockfileData(ParsedData):
    pex: PexLockfileData

    def get_info(self) -> LockfileInfo:
        return self.pex.get_info()


class PantsPexLockfileSchema(InputSchema):
    schema = "pants-pex"

    def parse(self, source: IO) -> ParsedData:
        header = CommentBlock(prefix="//").parse(source)
        metadata = Sections(delimiter="^--- ", keep=1).parse(header.source)
        return PantsPexLockfileData(
            raw=Format("json").parse(metadata.source).raw,
            pex=cast(PexLockfileData, Schema("pex").parse(source)),
        )
