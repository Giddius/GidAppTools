# region [Imports]

import pytest
from pytest import param
from pytest_lazyfixture import lazy_fixture
import pp
from pathlib import Path
import json
from gidapptools.gid_config.conversion.spec_data import SpecFile, SpecEntry, SpecSection, ConverterSpecData, SpecDataMissingError


# endregion[Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

# region [test_1]


basic_config_spec_result_items = {("first_section", "entry_one"): {"description": "",
                                                                   "converter": ConverterSpecData(typus="string", kw_arguments={}),
                                                                   "verbose_name": "Entry One",
                                                                   "implemented": True,
                                                                   "gui_visible": True},

                                  ("first_section", "entry_two"): {"converter": {"typus": "path", "kw_arguments": {}},
                                                                   "description": "this is the second entry description",
                                                                   "verbose_name": "2. Entry",
                                                                   "implemented": True,
                                                                   "gui_visible": True},

                                  ("first_section", "entry_three"): {"description": "",
                                                                     "converter": ConverterSpecData(typus="integer", kw_arguments={}),
                                                                     "verbose_name": "Entry Three",
                                                                     "implemented": True,
                                                                     "gui_visible": True},

                                  ("first_section", "does_not_exists"): {"error": SpecDataMissingError},

                                  ("third_section", "dynamic_entry"): {"converter": {"typus": "string", "kw_arguments": {}},
                                                                       "description": "",
                                                                       "verbose_name": "Dynamic Entry",
                                                                       "gui_visible": False,
                                                                       "implemented": True}}

test_get_spec_item_parameter = [param(lazy_fixture("basic_configspec_example_1"), basic_config_spec_result_items, id="basic_configspec_1")]


@ pytest.mark.parametrize(["in_spec_path", "results"], test_get_spec_item_parameter)
def test_get_spec_item(in_spec_path: Path, results: dict):
    spec = SpecFile(in_spec_path).reload()
    for entry_path, entry_attributes in results.items():
        if entry_attributes.get("error") is not None:
            with pytest.raises(entry_attributes["error"]):
                entry_item = spec.get_spec_entry(*entry_path)
        else:
            entry_item = spec.get_spec_entry(*entry_path)
            assert isinstance(entry_item, SpecEntry)
            for entry_attribute_name, entry_attribute_result in entry_attributes.items():
                assert getattr(entry_item, entry_attribute_name) == entry_attribute_result


# endregion [test_1]
