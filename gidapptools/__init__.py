"""
WiP
"""

from gidapptools.meta_data.interface import setup_meta_data, get_meta_info, get_meta_item, get_meta_paths
from gidapptools.gid_logger.logger import setup_main_logger, get_logger, setup_main_logger_with_file_logging, get_main_logger, get_handlers


__version__ = "0.4.4"


from pathlib import Path
from tzlocal import reload_localzone

THIS_FILE_DIR = Path(__file__).resolve().parent

# _log = logging.getLogger(__name__)
# _log.addHandler(logging.NullHandler())


def setup_library() -> None:
    from .gid_logger.logger import make_library_logger
    log = make_library_logger(__name__)
    log.debug("library %r setup", __name__)

    reload_localzone()


setup_library()
