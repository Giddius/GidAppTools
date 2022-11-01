
from gidapptools.errors import MissingOptionalDependencyError

with MissingOptionalDependencyError.try_import("peewee"):
    import peewee
