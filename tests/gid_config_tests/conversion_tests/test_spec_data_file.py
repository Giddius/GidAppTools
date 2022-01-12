import pytest
from pathlib import Path
from gidapptools.gid_config.conversion.spec_data import SpecFile, AdvancedDict, EntryTypus, SpecVisitor
from pprint import pprint

THIS_FILE_DIR = Path(__file__).parent.absolute()

simple_spec_file = THIS_FILE_DIR.joinpath("example_spec_file.json")


def test_spec_data_file_init():
    spec = SpecFile(simple_spec_file, visitor=SpecVisitor())
    assert spec.spec_name == "example_spec_file"


def test_load():
    spec = SpecFile(simple_spec_file, visitor=SpecVisitor())
    assert spec._data is None
    assert spec.last_size is None
    spec.load()
    assert spec.data is not None
    assert spec.last_size is not None
    assert set(spec.data) == {"first_section", "second_section", "third_section"}
    assert isinstance(spec['first_section']['first_key']["converter"], EntryTypus)
    all_end_values = []
    for section, entries in spec.items():
        for key, value in entries.items():
            all_end_values.append(value['converter'])
    assert all(isinstance(item, EntryTypus) for item in all_end_values)


def test_spec_attribute():
    spec = SpecFile(simple_spec_file, visitor=SpecVisitor())
    spec.load()
    assert spec.data["first_section"]["first_key"]["description"] == "This is the first key of the first section"
    assert spec.get_description("first_section", "first_key") == "This is the first key of the first section"
    assert spec.get_description("first_section", "missing_key") == ""
    assert spec.get_description("first_section", "second_key") == ""
