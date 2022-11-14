from io import StringIO

import toml

from lockfile_diff.base import Format


def test_parse_toml() -> None:
    data = dict(foo="bar")
    contents = StringIO(toml.dumps(data))
    res = Format("toml").parse(contents)
    assert res.raw == data
