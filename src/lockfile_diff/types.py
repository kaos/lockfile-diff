from __future__ import annotations

from dataclasses import dataclass
from typing import IO, Any, Iterable, Mapping, Union

from packaging.version import LegacyVersion, Version, parse

ParsedVersion = Union[Version, LegacyVersion]


@dataclass(frozen=True)
class LockfileInfo:
    dists: Mapping[str, ParsedVersion]

    @classmethod
    def create(cls, dists: Iterable[tuple[str, str]]) -> LockfileInfo:
        return cls(dists={name: parse(version) for name, version in dists})

    def diff(self, old: LockfileInfo) -> LockfileDiff:
        return LockfileDiff.create(old, self)


@dataclass(frozen=True)
class LockfileDiff:
    added: Mapping[str, ParsedVersion]
    removed: Mapping[str, ParsedVersion]
    unchanged: Mapping[str, ParsedVersion]
    upgraded: Mapping[str, tuple[ParsedVersion, ParsedVersion]]
    downgraded: Mapping[str, tuple[ParsedVersion, ParsedVersion]]

    @classmethod
    def create(cls, old: LockfileInfo, new: LockfileInfo) -> LockfileDiff:
        diff = {
            name: (old.dists[name], new.dists[name])
            for name in sorted({*old.dists.keys(), *new.dists.keys()})
            if name in old.dists and name in new.dists
        }
        return cls(
            added={name: version for name, version in new.dists.items() if name not in old.dists},
            removed={name: version for name, version in old.dists.items() if name not in new.dists},
            unchanged={name: curr for name, (prev, curr) in diff.items() if prev == curr},
            upgraded={name: (prev, curr) for name, (prev, curr) in diff.items() if prev < curr},
            downgraded={name: (prev, curr) for name, (prev, curr) in diff.items() if prev > curr},
        )


@dataclass(frozen=True)
class ParsedData:
    raw: Mapping[str, Any]

    @property
    def source(self) -> IO:
        raise NotImplementedError()

    def get_info(self) -> LockfileInfo:
        raise NotImplementedError()
