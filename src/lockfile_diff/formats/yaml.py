from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import IO, Any, overload

import yaml
from packaging.version import LegacyVersion, Version

from lockfile_diff.base import InputFormat, OutputFormat
from lockfile_diff.types import ParsedData


class YAMLDecoder(InputFormat):
    format = "yaml"

    def parse(self, contents: IO) -> ParsedData:
        return ParsedData(yaml.safe_load(contents))


class YAMLEncoder(OutputFormat):
    format = "yaml"

    @overload
    def encode(self, data: Any, dest: IO) -> None:
        ...

    @overload
    def encode(self, data: Any) -> str:
        ...

    def encode(self, data: Any, dest: IO | None = None) -> None | str:
        if is_dataclass(data):
            data = asdict(data)
        return yaml.safe_dump(data, dest)


def yaml_represent_version(dumper, data):
    return dumper.represent_str(str(data))


yaml.add_representer(Version, yaml_represent_version, Dumper=yaml.SafeDumper)
yaml.add_representer(LegacyVersion, yaml_represent_version, Dumper=yaml.SafeDumper)
