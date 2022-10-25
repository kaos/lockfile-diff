from __future__ import annotations

from collections import defaultdict
from functools import partial
from types import new_class
from typing import Any, Callable, cast

from lockfile_diff.util.class_registry.meta import RegistryType, T


def class_registry(
    cls: T | None = None, **traits: Callable[[type[T]], Any] | str
) -> RegistryType[T]:
    traits.setdefault("name", "__name__")
    if cls is None:
        return partial(class_registry, **traits)

    meta_namespace = dict(_RegistryType__classes=defaultdict(dict))
    metacls = new_class(
        f"{cls.__name__}Type", (RegistryType[T],), exec_body=lambda ns: ns.update(meta_namespace)
    )
    return cast(
        RegistryType[T], new_class(cls.__name__, (cls,), dict(metaclass=metacls, traits=traits))
    )
