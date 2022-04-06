from gidapptools.errors import MissingOptionalDependencyError


with MissingOptionalDependencyError.try_import("mdformat"):
    import mdformat


with MissingOptionalDependencyError.try_import("mdformat"):
    import mdformat
