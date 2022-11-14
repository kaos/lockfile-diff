from __future__ import annotations

from io import StringIO
from typing import IO, Iterator

import pytest
from class_registry import ClassRegistry

from lockfile_diff.base import InputSchema
from lockfile_diff.parser import Parser
from lockfile_diff.registries import Registries
from lockfile_diff.types import ParsedData


@pytest.fixture
def registries() -> Iterator[Registries]:
    old = Registries.set_default(Registries(ClassRegistry("format"), ClassRegistry("schema")))
    yield old
    Registries.set_default(old)


def test_parser_parse(registries: Registries) -> None:
    @registries.schemas.register
    class MockSchema(InputSchema):
        schema = "mock"

        def parse(self, source: IO) -> ParsedData:
            return ParsedData(dict(source=source))

    source = StringIO()
    res = Parser.parse(source, "mock")
    assert res.raw == dict(source=source)
