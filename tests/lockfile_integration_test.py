import re
from io import StringIO

import pytest

from lockfile_diff import formats, schemas  # noqa
from lockfile_diff.base import Format, Schema


@pytest.mark.parametrize(
    "input_file, expected_file",
    [
        (
            "tests/lockfiles/pex/cowsay-default.lock",
            "tests/lockfiles/pex/cowsay-default.test.yaml",
        ),
        (
            "tests/lockfiles/pants-pex/cowsay.lock",
            "tests/lockfiles/pants-pex/cowsay.test.yaml",
        ),
    ],
)
def test_lockfile_info(input_file: str, expected_file: str) -> None:
    m = re.match(r"^tests/lockfiles/(?P<schema>[^/]+)/.*\.(?P<format>.+)$", expected_file)
    assert m
    data = Schema(m.group("schema")).parse_file(input_file)
    info = data.get_info()
    actual = StringIO()
    Format(m.group("format")).encode(info, actual)
    with open(expected_file) as fd:
        expected = fd.read()
    assert actual.getvalue() == expected
