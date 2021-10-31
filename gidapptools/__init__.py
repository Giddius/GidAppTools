"""
WiP
"""

from gidapptools.meta_data.interface import setup_meta_data, get_meta_config, get_meta_info, get_meta_item, get_meta_paths


__version__ = "0.1.1"

try:
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())
except ImportError:
    pass
from pathlib import Path
THIS_FILE_DIR = Path(__file__).resolve().parent
