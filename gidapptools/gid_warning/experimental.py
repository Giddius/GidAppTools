"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path
from warnings import warn, warn_explicit
from functools import wraps

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def mark_experimental(extra_message: str = ""):
    def _wrapper(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            func_name = func.__qualname__ or func.__name__
            message = f"The function {func_name!r} is still experimentel and there is no guarantee that it works or does what it says.{extra_message}"
            try:
                warn_explicit(message=message, category=UserWarning, filename=func.__code__.co_filename, lineno=func.__code__.co_firstlineno, module=func.__module__)
            except Exception:
                warn(message=message, category=UserWarning, stacklevel=4)
            return func(*args, **kwargs)

        return _wrapped
    return _wrapper

# region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
