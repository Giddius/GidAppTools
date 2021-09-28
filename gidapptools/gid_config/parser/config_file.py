"""
WiP.

Soon.
"""

# region [Imports]


from enum import Enum
from pathlib import Path
from typing import Any, Literal, Mapping, Union
from hashlib import blake2b
from gidapptools.gid_config.parser.ini_parser import SimpleIniParser
from threading import Lock
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

CONFIG_SPEC_DATA_TYPE = dict[str, dict[str, Union[Any, None]]]


class ConfigFileTypus(Enum):
    INI = '.ini'
    JSON = '.json'


class ConfigFile:

    def __init__(self,
                 file_path: Path,
                 changed_parameter: Union[Literal['size'], Literal['file_hash']] = 'size',
                 parser: SimpleIniParser = None,
                 spec_data: CONFIG_SPEC_DATA_TYPE = None,
                 **kwargs) -> None:
        self.file_path = Path(file_path).resolve()
        self.config_typus = ConfigFileTypus(self.file_path.suffix)
        self.changed_parameter = changed_parameter
        self.parser = SimpleIniParser(**kwargs) if parser is None else parser(**kwargs)
        self.spec = {} if spec_data is None else spec_data
        self._size: int = None
        self._file_hash: str = None
        self._content: Mapping[str, Any] = None
        self.lock = Lock()

    @property
    def content(self) -> Mapping[str, Any]:
        with self.lock:
            if self._content is None or self.has_changed is True:
                self.load()
            return self._content

    @property
    def size(self) -> int:
        return self.file_path.stat().st_size

    @property
    def file_hash(self) -> str:
        _file_hash = blake2b()
        with self.file_path.open('rb') as f:
            for chunk in f:
                _file_hash.update(chunk)
        return _file_hash.hexdigest()

    @property
    def has_changed(self) -> bool:
        if self.changed_parameter == 'size':
            if self._size is None or self.size != self._size:
                return True
        elif self.changed_parameter == 'file_hash':
            if self._file_hash is None or self.file_hash != self._file_hash:
                return True
        return False

    def load(self) -> None:
        self._content = self.parser.parse(self.file_path)
        self._size = self.size
        self._file_hash = self.file_hash

    def write(self) -> None:
        with self.lock:
            with self.file_path.open('w', encoding='utf-8', errors='ignore') as f:
                header_comment = self.spec.get('header')
                if header_comment:
                    for line in header_comment.splitlines():
                        f.write(f"# {line}\n")
                    f.write("\n\n\n")
                for section, values in self._content.items():
                    section_comments = self.spec.get(section, {}).get('comments', [])
                    for comment in section_comments:
                        f.write(f"# {comment}\n")
                    f.write(f"[{section}]\n\n")
                    for key, value in values.items():
                        key_comments = self.spec.get(section, {}).get(key, {}).get('comments', [])
                        for comment in key_comments:
                            f.write(f"# {comment}\n")
                        f.write(f"{key} = {value}\n")
                    f.write('\n\n')
            self.load()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
