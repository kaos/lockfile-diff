from __future__ import annotations

from typing import IO

import toml

from lockfile_diff.base import InputFormat
from lockfile_diff.types import ParsedData


class TOML(InputFormat):
    format = "toml"

    def parse(self, contents: IO) -> ParsedData:
        return ParsedData(toml.load(contents))
