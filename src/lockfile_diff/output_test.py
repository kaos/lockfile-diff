from unittest.mock import Mock

import pytest
from packaging.version import parse

from lockfile_diff.output import Text


@pytest.fixture(autouse=True)
def patch_click_style(monkeypatch):
    monkeypatch.setattr("lockfile_diff.output.style", Mock(side_effect=lambda txt, **kw: txt))


@pytest.mark.parametrize(
    "prev, curr, expected",
    [
        ("1.0.0", "1.0.1", ">"),
        ("1.0.0", "1.1.0", "-->"),
        ("1.0.0", "2.0.0", "==>"),
        ("1", "1.0.1", ">"),
        ("1.0.1", "1.0.0", "<"),
        ("1.1.0", "1.0.0", "<--"),
        ("2.0.0", "1.0.0", "<=="),
        ("1.0.1", "1", "<"),
    ],
)
def test_text_get_bump_s(prev: str, curr: str, expected: str) -> None:
    assert Text.get_bump_s(parse(prev), parse(curr)).strip() == expected
