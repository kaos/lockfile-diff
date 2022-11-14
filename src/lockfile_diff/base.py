from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import IO, Any, ClassVar, Mapping, overload

from lockfile_diff.registries import AutoRegister, Registries, RegistryBase
from lockfile_diff.types import ParsedData


class InputBase(ABC, RegistryBase):
    @abstractmethod
    def parse(self, source: IO) -> ParsedData:
        raise NotImplementedError()


class OutputBase(ABC, RegistryBase):
    @overload
    def encode(self, data: Any, dest: IO) -> None:
        ...

    @overload
    def encode(self, data: Any) -> str:
        ...

    @abstractmethod
    def encode(self, data: Any, dest: IO | None = None) -> None | str:
        raise NotImplementedError()


class InputFormat(InputBase, metaclass=AutoRegister(lambda: Registries.get_default().input_formats)):  # type: ignore[misc]
    kind = "input_formats"
    format: ClassVar[str]


class OutputFormat(OutputBase, metaclass=AutoRegister(lambda: Registries.get_default().output_formats)):  # type: ignore[misc]
    kind = "output_formats"
    format: ClassVar[str]


class InputSchema(InputBase, metaclass=AutoRegister(lambda: Registries.get_default().schemas)):  # type: ignore[misc]
    kind = "schemas"
    schema: ClassVar[str]


@dataclass
class InputOutputHelper:
    name: str
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    @property
    def input(self) -> InputBase:
        raise NotImplementedError()

    @property
    def output(self) -> OutputBase:
        raise NotImplementedError()

    def parse_file(self, filename: str) -> ParsedData:
        with open(filename) as fd:
            return self.parse(fd)

    def parse(self, source: IO) -> ParsedData:
        return self.input.parse(source)

    @overload
    def encode(self, data: Any, dest: IO) -> None:
        ...

    @overload
    def encode(self, data: Any) -> str:
        ...

    def encode(self, data: Any, dest: IO | None = None) -> None | str:
        return self.output.encode(data, dest)  # type: ignore[arg-type]


class Format(InputOutputHelper):
    @property
    def input(self) -> InputBase:
        return InputFormat.get(self.name, *self.args, **self.kwargs)

    @property
    def output(self) -> OutputBase:
        return OutputFormat.get(self.name, *self.args, **self.kwargs)


class Schema(InputOutputHelper):
    @property
    def input(self) -> InputBase:
        return InputSchema.get(self.name, *self.args, **self.kwargs)
