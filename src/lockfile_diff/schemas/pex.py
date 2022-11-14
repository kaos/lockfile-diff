from __future__ import annotations

import itertools
from collections import namedtuple
from dataclasses import dataclass
from typing import IO, Sequence

from lockfile_diff.base import Format, InputSchema
from lockfile_diff.types import LockfileInfo, ParsedData

LockedResolve = namedtuple("LockedResolve", ("locked_requirements"))
LockedRequirement = namedtuple("LockedRequirement", ("project_name", "version"))


@dataclass(frozen=True)
class PexLockfileData(ParsedData):
    locked_resolves: Sequence[LockedResolve]

    @classmethod
    def create(cls, parsed_data: ParsedData) -> PexLockfileData:
        """NOTICE.

        The pex lockfile format is an internal implementation detail in pex and subject to change
        without notice.

        We have been warned.
        """
        if "pex_version" not in parsed_data.raw:
            raise ValueError("not a pex lockfile")

        return cls(
            parsed_data.raw,
            locked_resolves=tuple(
                LockedResolve(
                    locked_requirements=tuple(
                        LockedRequirement(
                            project_name=requirement["project_name"],
                            version=requirement["version"],
                        )
                        for requirement in resolve["locked_requirements"]
                    ),
                )
                for resolve in parsed_data.raw["locked_resolves"]
            ),
        )

    def get_info(self) -> LockfileInfo:
        return LockfileInfo.create(
            (req.project_name, req.version)
            for req in itertools.chain.from_iterable(
                resolve.locked_requirements for resolve in self.locked_resolves
            )
        )


class PexLockfileSchema(InputSchema):
    schema = "pex"

    def parse(self, source: IO) -> ParsedData:
        return PexLockfileData.create(Format("json").parse(source))
