from __future__ import annotations

from typing import Any

from lockfile_diff.info import LockfileInfo
from lockfile_diff.util.class_registry.decorator import class_registry
from lockfile_diff.util.class_registry.meta import get_implementation


@class_registry(kind="data_type")
class DataRegistry:
    @classmethod
    def get_info(cls, data: Any) -> LockfileInfo:
        return get_implementation(cls, kind=type(data)).get_info(data)
