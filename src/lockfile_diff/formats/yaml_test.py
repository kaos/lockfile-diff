from io import StringIO

import yaml

from lockfile_diff.base import Format


def test_parse_yaml() -> None:
    data = dict(foo="bar")
    contents = StringIO(yaml.safe_dump(data))
    res = Format("yaml").parse(contents)
    assert res.raw == data
