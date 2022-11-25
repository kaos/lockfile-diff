from __future__ import annotations

import os.path
from dataclasses import dataclass
from typing import IO, Sequence, cast
from zipfile import ZipFile

from lockfile_diff.base import Format, InputSchema
from lockfile_diff.types import LockfileInfo, ParsedData


@dataclass(frozen=True)
class PexInfoData(ParsedData):
    distributions: Sequence[str]

    @classmethod
    def create(cls, parsed_data: ParsedData) -> PexInfoData:
        if "pex_version" not in parsed_data.raw.get("build_properties", {}):
            raise ValueError("not a PEX-INFO file")

        return cls(parsed_data.raw, distributions=tuple(parsed_data.raw["distributions"].keys()))

    def get_info(self) -> LockfileInfo:
        return LockfileInfo.create(
            cast("tuple[str, str]", tuple(dist.split("-")[:2]))
            for dist in self.distributions
            if "-" in dist
        )


class PexInfoSchema(InputSchema):
    schema = "pex-info"

    def parse(self, source: IO) -> ParsedData:
        return PexInfoData.create(Format("json").parse(source))


class PexAppSchema(InputSchema):
    schema = "pex-app"

    def parse(self, source: IO) -> ParsedData:
        filename = getattr(source, "name", str(source))
        if not os.path.isfile(filename):
            raise ValueError(f"input must be a file on disk, got {filename}")

        with ZipFile(filename) as zf:
            with zf.open("PEX-INFO") as pi:
                return PexInfoSchema().parse(pi)
