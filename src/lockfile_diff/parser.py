from __future__ import annotations

from typing import IO

from lockfile_diff.base import Schema
from lockfile_diff.types import LockfileDiff, ParsedData


class Parser:
    @staticmethod
    def parse(source: IO, schema: str, **kwargs) -> ParsedData:
        return Schema(schema, kwargs=kwargs).parse(source)

    @classmethod
    def diff(cls, old_source: IO, new_source: IO, schema: str, **kwargs) -> LockfileDiff:
        return LockfileDiff.create(
            cls.parse(old_source, schema, **kwargs).get_info(),
            cls.parse(new_source, schema, **kwargs).get_info(),
        )
