lockfile-diff
=============

[![version](https://img.shields.io/pypi/v/lockfile-diff.svg)](https://pypi.org/project/lockfile-diff)

Print a summary of what have changed in a given lockfile.


Currently supports the lockfile format used by [`pex`](https://pypi.org/project/pex) (which is an
internal format subject to change without notice) and [`Coursier`](https://get-coursier.io/),
support for more lockfile formats are planned, also for other eco systems besides Python and
Java. (JavaScript, Rust, Go, ...)

Does also support reading the distributions included in a `.pex` app.


License
=======

Provided under the [MIT](https://opensource.org/licenses/MIT) license, as "public domain" is not an
OSI approved license.
