from __future__ import annotations

from abc import ABCMeta
from dataclasses import dataclass
from inspect import isabstract
from typing import Callable, ClassVar, TypeVar, cast

from class_registry import ClassRegistry, MutableRegistry

T = TypeVar("T", bound="RegistryBase")

_default_registries: Registries


@dataclass(frozen=True)
class Registries:
    input_formats: ClassRegistry = ClassRegistry("format")
    output_formats: ClassRegistry = ClassRegistry("format")
    schemas: ClassRegistry = ClassRegistry("schema")

    @staticmethod
    def get_default() -> Registries:
        return _default_registries

    @staticmethod
    def set_default(registries: Registries) -> Registries:
        global _default_registries
        was = _default_registries
        _default_registries = registries
        return was


class RegistryBase:
    kind: ClassVar[str]

    @classmethod
    def get(cls: type[T], name: str, *args, **kwargs) -> T:
        return cast(T, getattr(_default_registries, cls.kind).get(name, *args, **kwargs))


_default_registries = Registries()


def AutoRegister(registry_cb: Callable[[], MutableRegistry], base_type: type = ABCMeta) -> type:
    """Creates a metaclass that automatically registers all non-abstract
    subclasses in the specified registry.

    Adapted from `class_registry.AutoRegistry` to take a callback for
    the registry arg to make it more dynamic.
    """

    class _metaclass(base_type):  # type: ignore[valid-type, misc]
        def __init__(self, what, bases=None, attrs=None):
            registry = registry_cb()
            if not registry.attr_name:
                raise ValueError(
                    "Missing `attr_name` in {registry}.".format(registry=registry),
                )

            super(_metaclass, self).__init__(what, bases, attrs)

            if not isabstract(self):
                registry.register(self)

    return _metaclass
