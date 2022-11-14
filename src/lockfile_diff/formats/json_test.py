import json
from io import StringIO

from lockfile_diff.base import Format


def test_parse_json() -> None:
    data = dict(foo="bar")
    contents = StringIO(json.dumps(data))
    res = Format("json").parse(contents)
    assert res.raw == data
