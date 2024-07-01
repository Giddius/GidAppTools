from gidapptools.errors import MissingOptionalDependencyError


MissingOptionalDependencyError.check_is_importable("PySide6")


MissingOptionalDependencyError.check_is_importable("jinja2")
