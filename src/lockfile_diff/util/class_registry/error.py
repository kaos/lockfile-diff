class ClassRegistryError(Exception):
    pass


class ClassRegistryImplementationNotFoundError(ClassRegistryError):
    pass


class ClassRegistryUnknownSelectionTraitError(ClassRegistryError):
    pass
