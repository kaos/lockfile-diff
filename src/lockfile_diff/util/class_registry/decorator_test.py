from lockfile_diff.util.class_registry.decorator import class_registry


def test_class_registry_decorator() -> None:
    @class_registry
    class TestRegistry:
        pass

    @class_registry
    class OtherRegistry:
        pass

    class Test1(TestRegistry):
        pass

    class Test2(TestRegistry):
        pass

    assert TestRegistry._RegistryType__classes == {  # type: ignore[attr-defined]
        "name": {
            "TestRegistry": TestRegistry,
            "Test1": Test1,
            "Test2": Test2,
        },
    }
    assert OtherRegistry._RegistryType__classes == {  # type: ignore[attr-defined]
        "name": {
            "OtherRegistry": OtherRegistry,
        },
    }
