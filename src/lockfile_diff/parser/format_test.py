import json
from io import StringIO

from lockfile_diff.parser.format import JSON, CommentBlock, Sections


def test_parse_json() -> None:
    data = dict(foo="bar", baz=123)
    content = StringIO(json.dumps(data))
    assert JSON.parse(content) == data


def test_parse_commented_block() -> None:
    data = """\
// This is a line
//
// And another.
// more
//  -- here.
//
"""
    expected = """\
This is a line

And another.
more
 -- here.

"""
    assert CommentBlock.parse(StringIO(data)).read() == expected


def test_parse_sections() -> None:
    data = """\
This is
the first section

And here
next to it
the other one.
"""
    actual = [s.read() for s in Sections.parse(StringIO(data))]
    assert actual == ["This is\nthe first section\n", "And here\nnext to it\nthe other one.\n"]
