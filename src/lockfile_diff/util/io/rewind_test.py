from io import StringIO
from typing import IO

import pytest

from lockfile_diff.util.io.rewind import capture


@pytest.fixture
def data() -> IO:
    stream = StringIO(
        """some
        lines of
        text.
        """
    )
    return stream


def test_capture_rewind(data: IO) -> None:
    with capture(data) as c:
        assert data.readline() == "some\n"
        assert data.tell() == 5
        c.rewind()
        assert data.tell() == 0


def test_rewind_on_error(data: IO) -> None:
    with pytest.raises(Exception):
        with capture(data):
            assert data.readline() == "some\n"
            assert data.tell() == 5
            raise Exception()
    assert data.tell() == 0


def test_rewind_on_exit(data: IO) -> None:
    with capture(data):
        assert data.readline() == "some\n"
        assert data.tell() == 5
    assert data.tell() == 0


def test_rewind_to_last_commit(data: IO) -> None:
    with capture(data) as c:
        assert data.readline() == "some\n"
        assert data.tell() == 5
        c.commit()
        assert data.readline().strip() == "lines of"
        assert data.tell() == 22
    assert data.tell() == 5


def test_no_rewind_on_release(data: IO) -> None:
    with capture(data) as c:
        assert data.readline() == "some\n"
        assert data.tell() == 5
        c.release()
    assert data.tell() == 5
