from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import IO, ClassVar, cast

import click

from lockfile_diff.base import InputSchema
from lockfile_diff.errors import FAILED_TO_PARSE_FILE
from lockfile_diff.registries import Registries
from lockfile_diff.types import ParsedData
from lockfile_diff.util.io.rewind import capture


@dataclass(frozen=True)
class AutoDetectSchema(InputSchema):
    schema: ClassVar[str] = "auto-detect"
    quiet: bool = False

    def parse(self, source: IO) -> ParsedData:
        errors = []
        for schema_cls in Registries.get_default().schemas.values():
            if schema_cls is AutoDetectSchema:
                continue
            try:
                with capture(source):
                    return cast(InputSchema, schema_cls()).parse(source)
            except Exception as e:
                errors.append(f"  - `{schema_cls.schema}`: {e}")

        if self.quiet:
            sys.exit(0)

        click.echo(
            (
                f"ERROR: `auto-detect` failed to parse {getattr(source, 'name', str(source))!r} with "
                "any of the following schemas:"
            ),
            err=True,
        )
        click.echo("\n".join(errors), err=True)
        sys.exit(FAILED_TO_PARSE_FILE)
