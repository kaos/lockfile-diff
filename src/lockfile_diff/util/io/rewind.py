from __future__ import annotations

from contextlib import contextmanager
from typing import IO, Iterator


class CaptureState:
    def __init__(self, io: IO) -> None:
        assert io.seekable()
        self.__io: IO | None = io
        self.__captured_pos = io.tell()

    def commit(self) -> None:
        if self.__io is not None:
            self.__captured_pos = self.__io.tell()

    def release(self) -> None:
        self.__io = None

    def rewind(self) -> None:
        if self.__io is not None:
            self.__io.seek(self.__captured_pos)


@contextmanager
def capture(io: IO) -> Iterator[CaptureState]:
    state = CaptureState(io)
    try:
        yield state
    finally:
        state.rewind()
