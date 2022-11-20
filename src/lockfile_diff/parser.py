from __future__ import annotations

from typing import IO

from lockfile_diff.base import Schema
from lockfile_diff.types import LockfileDiff, LockfileInfo, ParsedData


class EmptyData(ParsedData):
    def get_info(self) -> LockfileInfo:
        return LockfileInfo({})


class Parser:
    @staticmethod
    def parse(source: IO | None, schema: str, **kwargs) -> ParsedData:
        if source is None:
            return EmptyData({})
        else:
            return Schema(schema, kwargs=kwargs).parse(source)

    @classmethod
    def diff(
        cls, old_source: IO | None, new_source: IO | None, schema: str, **kwargs
    ) -> LockfileDiff:
        return LockfileDiff.create(
            cls.parse(old_source, schema, **kwargs).get_info(),
            cls.parse(new_source, schema, **kwargs).get_info(),
        )
