from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import IO, Any, Mapping

from lockfile_diff.core import DataRegistry
from lockfile_diff.info import LockfileInfo
from lockfile_diff.parser.format import Format


@dataclass
class PexLockfileData:
    metadata: Mapping[str, Any]
    pex_lock: Mapping[str, Any]


class PantsPexLockfile(Format):
    format = "pants-pex"

    @classmethod
    def parse(cls, content: IO) -> PexLockfileData:
        header, body = cls.chain(name="Sections").parse(content)
        metadata = (
            cls.chain(name="CommentBlock")
            .chain(
                dict(
                    section_delimiter="^---",
                    select_section=1,
                ),
                name="Sections",
            )
            .chain(
                name="JSON",
            )
            .parse(header)
        )

        return PexLockfileData(
            metadata=metadata,
            pex_lock=cls.chain(name="JSON").parse(body),
        )


class PexLockfileDataConverter(DataRegistry):
    data_type = PexLockfileData

    @classmethod
    def get_info(cls, data: PexLockfileData) -> LockfileInfo:
        """NOTICE.

        The pex lockfile format is an internal implementation detail in pex and subject to change
        without notice.

        We have been warned.
        """
        all_locked_requirements = (
            resolve.get("locked_requirements", [])
            for resolve in data.pex_lock.get("locked_resolves", [])
        )
        return LockfileInfo.create(
            (locked["project_name"], locked["version"])
            for locked in itertools.chain.from_iterable(all_locked_requirements)
        )
