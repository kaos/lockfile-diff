from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import IO, Any, overload

from packaging.version import LegacyVersion, Version

from lockfile_diff.base import InputFormat, OutputFormat
from lockfile_diff.types import ParsedData


class JSONDecoder(InputFormat):
    format = "json"

    def parse(self, source: IO) -> ParsedData:
        return ParsedData(json.load(source))


class JSONEncoder(OutputFormat):
    format = "json"

    @overload
    def encode(self, data: Any, dest: IO) -> None:
        ...

    @overload
    def encode(self, data: Any) -> str:
        ...

    def encode(self, data: Any, dest: IO | None = None) -> None | str:
        if dest is None:
            return json.dumps(data, cls=_JSONEncoder)
        json.dump(data, dest, cls=_JSONEncoder)
        return None


class _JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (LegacyVersion, Version)):
            return str(o)
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)
