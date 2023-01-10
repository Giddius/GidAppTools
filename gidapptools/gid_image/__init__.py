from gidapptools.errors import MissingOptionalDependencyError


with MissingOptionalDependencyError.try_import("PIL"):
    import PIL
