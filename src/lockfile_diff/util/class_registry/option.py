import click

from lockfile_diff.util.class_registry.meta import ClassRegistry, get_trait_values


def class_registry_option(cls: ClassRegistry, *args, trait: str, **kwargs):
    if not args:
        args = (f"--{trait}",)
    return click.option(*args, type=click.Choice(get_trait_values(cls, trait)), **kwargs)
