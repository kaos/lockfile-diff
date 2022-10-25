from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from packaging.version import Version, parse


@dataclass
class LockfileInfo:
    dists: Mapping[str, Version]

    @classmethod
    def create(cls, dists: Iterable[tuple[str, str]]) -> LockfileInfo:
        return cls(dists={name: parse(version) for name, version in dists})

    def diff(self, old: LockfileInfo) -> LockfileDiff:
        return LockfileDiff.create(old, self)


@dataclass
class LockfileDiff:
    added: Mapping[str, Version]
    removed: Mapping[str, Version]
    unchanged: Mapping[str, Version]
    upgraded: Mapping[str, tuple[Version, Version]]
    downgraded: Mapping[str, tuple[Version, Version]]

    @classmethod
    def create(cls, old: LockfileInfo, new: LockfileInfo) -> LockfileDiff:
        diff = {
            name: (old.dists.get(name), new.dists.get(name))
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
