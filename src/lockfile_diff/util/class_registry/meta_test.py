import pytest

from lockfile_diff.util.class_registry.decorator import class_registry
from lockfile_diff.util.class_registry.error import ClassRegistryImplementationNotFoundError
from lockfile_diff.util.class_registry.meta import get_implementation, get_trait_values, get_traits


def test_get_implementation() -> None:
    @class_registry
    class TestRegistry:
        pass

    class Test1(TestRegistry):
        pass

    class Test2(TestRegistry):
        pass

    assert get_implementation(TestRegistry, name="Test1") == Test1
    assert get_implementation(TestRegistry, name="Test2") == Test2
    assert get_implementation(TestRegistry, name="Alias", default=Test2) == Test2
    with pytest.raises(ClassRegistryImplementationNotFoundError):
        get_implementation(TestRegistry, name="missing")


def test_class_selection() -> None:
    @class_registry(key="test_key")
    class TestRegistry:
        pass

    class Test1(TestRegistry):
        test_key = "one"

    class Test2(TestRegistry):
        test_key = "two"

    assert get_traits(TestRegistry) == ("key", "name")
    assert get_trait_values(TestRegistry, "key") == ("one", "two")
    assert get_trait_values(TestRegistry, "name") == ("TestRegistry", "Test1", "Test2")

    assert get_implementation(TestRegistry, key="one") == Test1
    assert get_implementation(TestRegistry, key="two") == Test2
    with pytest.raises(ClassRegistryImplementationNotFoundError):
        get_implementation(TestRegistry, key="missing")
    with pytest.raises(ClassRegistryImplementationNotFoundError):
        get_implementation(TestRegistry, blip="one")

    # Default trait still available.
    assert get_implementation(TestRegistry, name="Test1") == Test1
