from __future__ import annotations

from operator import attrgetter
from typing import Any, Callable, DefaultDict, Generic, Mapping, TypeVar

from lockfile_diff.util.class_registry.error import (
    ClassRegistryImplementationNotFoundError,
    ClassRegistryUnknownSelectionTraitError,
)

T = TypeVar("T", bound=type)


class RegistryType(Generic[T], type):
    __classes: DefaultDict[str, dict[Any, type[T]]]
    __traits: Mapping[str, Callable[[type[T]], Any]]

    def __new__(metacls, classname, bases, classdict, traits=None, **kwds):
        cls = super().__new__(metacls, classname, bases, classdict, **kwds)
        if traits is not None:
            metacls.__traits = traits
        for trait, cb in metacls.__traits.items():
            if isinstance(cb, str):
                cb = attrgetter(cb)
                metacls.__traits[trait] = cb
            try:
                metacls.__classes[trait][cb(cls)] = cls
            except AttributeError:
                pass
        return cls


ClassRegistry = RegistryType[T]


def get_traits(cls: ClassRegistry) -> tuple[str, ...]:
    return tuple(cls._RegistryType__classes.keys())


def get_trait_values(cls: ClassRegistry, trait: str) -> tuple[str, ...]:
    return tuple(cls._RegistryType__classes[trait].keys())


def get_trait_implementations(cls: ClassRegistry, trait: str) -> tuple[str, ...]:
    return tuple(cls._RegistryType__classes[trait].values())


def get_implementation(
    cls: ClassRegistry, *, default: type[T] | None = None, **selection
) -> type[T]:
    if not selection:
        raise ClassRegistryUnknownSelectionTraitError("missing trait selection criteria")

    for trait, value in selection.items():
        impl = cls._RegistryType__classes[trait].get(value)
        if impl is not None:
            return impl

    if default is not None:
        return default

    raise ClassRegistryImplementationNotFoundError(f"{cls}: {selection}")
