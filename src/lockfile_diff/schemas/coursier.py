from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass
from typing import IO, Sequence

from lockfile_diff.base import Format, InputSchema
from lockfile_diff.types import LockfileInfo, ParsedData

Entry = namedtuple("Entry", ("artifact", "version"))


@dataclass(frozen=True)
class CoursierLockfileData(ParsedData):
    entries: Sequence[Entry]

    @classmethod
    def create(cls, parsed_data: ParsedData) -> CoursierLockfileData:
        if "entries" not in parsed_data.raw:
            raise ValueError("not a coursier lockfile")
        return cls(
            parsed_data.raw,
            entries=tuple(
                Entry(
                    artifact=entry["coord"]["artifact"],
                    version=entry["coord"]["version"],
                )
                for entry in parsed_data.raw["entries"]
            ),
        )

    def get_info(self) -> LockfileInfo:
        return LockfileInfo.create((entry.artifact, entry.version) for entry in self.entries)


class CoursierLockfileSchema(InputSchema):
    schema = "coursier"

    def parse(self, source: IO) -> ParsedData:
        return CoursierLockfileData.create(Format("toml").parse(source))
