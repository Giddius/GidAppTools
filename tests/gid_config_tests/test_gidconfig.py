import pytest
from pathlib import Path
from gidapptools.gid_config.interface import GidIniConfig
from gidapptools.gid_config.parser.config_data import ConfigFile, BaseIniParser
from gidapptools.gid_config.conversion.spec_data import SpecFile, SpecVisitor
from gidapptools.errors import SectionExistsError, SectionMissingError, ValueValidationError
from gidapptools.gid_config.conversion.entry_typus_item import EntryTypus
from pprint import pprint
import os
import re

from datetime import timedelta


def test_gid_ini_config_general(example_config_1: Path, example_spec_1: Path):
    config = GidIniConfig(config_file=ConfigFile(example_config_1, BaseIniParser()), spec_file=SpecFile(example_spec_1, SpecVisitor()))
    config.reload()
    assert config.get("debug", "a_value_with_spaces") == "this is a test"
    assert config.as_dict() == {'debug': {'current_testing_channel': 'bot-testing', "a_value_with_spaces": "this is a test"},
                                'folder': {'folder_1': Path('C:/Program Files/Git/cmd')},
                                'general_settings': {'cogs_location': 'antipetros_discordbot.cogs',
                                                     'guild_id': 449481990513754112,
                                                     'main_folder_name': 'antipetros_discordbot',
                                                     'owner_ids': [122348088319803392,
                                                                   346595708180103170,
                                                                   262095121527472128,
                                                                   225100859674066945],
                                                     "empty_entry": None},
                                'this': {'something': 'blah', 'that': 40},
                                "data_types": {"this_is_a_boolean": True}}

    assert config.as_dict(raw=True) == {'debug': {'current_testing_channel': 'bot-testing', "a_value_with_spaces": "this is a test"},
                                        'folder': {'folder_1': 'C:\\Program Files\\Git\\cmd'},
                                        'general_settings': {'cogs_location': 'antipetros_discordbot.cogs',
                                                             'guild_id': '449481990513754112',
                                                             'main_folder_name': 'antipetros_discordbot',
                                                             'owner_ids': '122348088319803392, 346595708180103170, '
                                                             '262095121527472128, 225100859674066945',
                                                             "empty_entry": None},
                                        'this': {'something': 'blah', 'that': '40'},
                                        "data_types": {"this_is_a_boolean": "yes"}}
    config.reload()


def test_gid_ini_config_sections(gid_ini_config: GidIniConfig):
    config_changes = 0

    def config_has_changed(*args):
        nonlocal config_changes
        config_changes += 1

    gid_ini_config.reload()
    gid_ini_config.config.changed_signal.connect(config_has_changed)
    assert len(gid_ini_config.config.all_sections) == 6
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "debug", "this", "folder", '__ENV__', 'data_types'}
    gid_ini_config.add_section('a_new_section')
    assert len(gid_ini_config.config.all_sections) == 7
    assert config_changes == 1
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "debug", "this", "folder", "a_new_section", '__ENV__', 'data_types'}

    gid_ini_config.add_section("this")
    with pytest.raises(SectionExistsError):
        gid_ini_config.add_section("this", existing_ok=False)
    gid_ini_config.remove_section("debug")
    assert gid_ini_config.get("this", "something") == "blah"
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "this", "folder", "a_new_section", '__ENV__', 'data_types'}
    assert len(gid_ini_config.config.all_sections) == 6

    assert config_changes == 2
    with pytest.raises(SectionMissingError):
        gid_ini_config.remove_section("debug", False)


def test_gid_ini_config_set(gid_ini_config: GidIniConfig):
    gid_ini_config.reload()
    gid_ini_config.set("this", "that", 5)
    assert gid_ini_config.get("this", "that") == 5


def test_gid_ini_config_get_section(gid_ini_config: GidIniConfig):
    debug_section = gid_ini_config.get_section('debug')
    assert debug_section == {'current_testing_channel': 'bot-testing', "a_value_with_spaces": "this is a test"}
    general_settings_section = gid_ini_config.get_section('general_settings')
    assert general_settings_section == {'cogs_location': 'antipetros_discordbot.cogs',
                                        'guild_id': 449481990513754112,
                                        'main_folder_name': 'antipetros_discordbot',
                                        'owner_ids': [122348088319803392,
                                                      346595708180103170,
                                                      262095121527472128,
                                                      225100859674066945],
                                        "empty_entry": None}


def test_env_get(gid_ini_config: GidIniConfig):
    gid_ini_config.reload()
    x = gid_ini_config.get('__ENV__', "PATH")
    assert set(x) == {Path(item.strip()) for item in os.getenv('PATH').split(';') if item.strip()}


def test_gid_ini_config_get(gid_ini_config: GidIniConfig):
    assert gid_ini_config.get("debug", "current_testing_channel") == "bot-testing"
    assert gid_ini_config.get("general_settings", "guild_id") == 449481990513754112
    assert gid_ini_config.get("folder", "folder_1") == Path(r"C:\Program Files\Git\cmd")

    assert gid_ini_config.get("debug", 'not_existing', fallback_entry=("general_settings", "guild_id")) == 449481990513754112

    assert gid_ini_config.get("debug", 'not_existing', default=12345) == 12345

    assert gid_ini_config.get("debug", 'not_existing', fallback_entry=("general_settings", "also_missing"), default=56789) == 56789


def test_gid_ini_config_2_get(gid_ini_config_2: GidIniConfig):
    assert gid_ini_config_2.get("debug", "current_testing_channel") == "bot-testing"
    assert gid_ini_config_2.get("general_settings", "guild_id") == 449481990513754112
    assert gid_ini_config_2.get("folder", "folder_1") == Path(r"C:\Program Files\Git\cmd")

    assert gid_ini_config_2.get("debug", 'not_existing', fallback_entry=("general_settings", "guild_id")) == 449481990513754112

    assert gid_ini_config_2.get("debug", 'not_existing', default=12345) == 12345

    assert gid_ini_config_2.get("debug", 'not_existing', fallback_entry=("general_settings", "also_missing"), default=56789) == 56789

    assert gid_ini_config_2.get("this", "max_threads", default=None) is None
    assert gid_ini_config_2.get("this", "max_update_time_frame", default=None) == timedelta(days=3)


def test_string_sub_arguments(gid_ini_config_3: GidIniConfig):
    typus: EntryTypus = gid_ini_config_3.spec.get_spec_attribute("string_subargs", "this_has_choices", "converter")
    assert typus.base_typus == str
    assert typus.named_arguments == {"choices": ["alpha", "beta"]}

    typus: EntryTypus = gid_ini_config_3.spec.get_spec_attribute("string_subargs", "choices_with_empty", "converter")
    assert typus.base_typus == str
    assert typus.named_arguments == {"choices": ["prima", "secundus"]}

    typus: EntryTypus = gid_ini_config_3.spec.get_spec_attribute("string_subargs", "choices_with_wrong_value", "converter")
    assert typus.base_typus == str
    assert typus.named_arguments == {"choices": ["start", "end"]}

    assert gid_ini_config_3.get("string_subargs", "this_has_choices") == 'alpha'

    assert gid_ini_config_3.get("string_subargs", "choices_with_empty") is None

    with pytest.raises(ValueValidationError, match=re.escape(r"""Value 'middle' with Base-Typus <class 'str'> failed its validation, value needs to be one of ['start', 'end']""")):
        gid_ini_config_3.get("string_subargs", "choices_with_wrong_value")

    assert gid_ini_config_3.get("string_subargs", "choices_with_wrong_value", default="the_default") == "the_default"


def test_descriptions(gid_ini_config_3: GidIniConfig):
    assert gid_ini_config_3.get_description("debug", "current_testing_channel") == "This is a description."


def test_empty_config(gid_ini_config_empty: GidIniConfig):
    gid_ini_config_empty.reload()
    assert gid_ini_config_empty.get("a_section", "a_key") == "this is a default"
    assert gid_ini_config_empty.get("a_section", "a_key", default="this is a manual default") == "this is a manual default"

    assert gid_ini_config_empty.get("a_section_not_in_spec", "a_key_not_in_spec", default="this is a default not in spec") == "this is a default not in spec"

    with pytest.raises(SectionMissingError):
        gid_ini_config_empty.get("a_section_not_in_spec", "a_key_not_in_spec")

    gid_ini_config_empty.set("a_created_section", "a_created_key", True, create_missing_section=True)

    assert gid_ini_config_empty.get("a_created_section", "a_created_key", default=False) is True


def test_non_existing_config_file(non_existing_config: Path, example_empty_config_spec: Path):
    assert non_existing_config.exists() is False
    assert example_empty_config_spec.exists() is True

    config = GidIniConfig(config_file=non_existing_config, spec_file=example_empty_config_spec)

    assert config.get("a_section", "a_key") == "this is a default"

    assert non_existing_config.exists() is True


def test_non_existing_config_file_prefill(non_existing_config: Path, example_spec_4: Path):
    assert non_existing_config.exists() is False
    assert example_spec_4.exists() is True

    config = GidIniConfig(config_file=non_existing_config, spec_file=example_spec_4, fill_missing_with_defaults=True)
    assert config.config.has_section("this") is True
    assert config.config.has_section("folder") is False

    assert config.config.has_key("this", "that") is True

    assert config.config.has_key("folder", "folder_1") is False

    assert config.config.has_key("general_settings", "empty_entry") is False

    assert config.get("this", "that") == 48

    assert config.get("general_settings", "owner_ids") == [123, 456]

    assert config.get("this", "max_update_time_frame") == timedelta(days=0, hours=3, minutes=5, milliseconds=0, microseconds=0, weeks=0)

    assert non_existing_config.exists() is True

    expected_lines = ["[debug]",
                      "current_testing_channel = default_testing_channel",
                      "[general_settings]",
                      "cogs_location = default_cogs_location",
                      "main_folder_name = default_main_folder_name",
                      "owner_ids = 123, 456",
                      "[this]",
                      "that = 48",
                      "max_update_time_frame = 3 hours 5 minutes"]

    assert [l for l in non_existing_config.read_text(encoding='utf-8', errors='ignore').splitlines() if l] == expected_lines
