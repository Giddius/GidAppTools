import pytest
from pathlib import Path
from gidapptools.gid_config.interface import GidIniConfig
from gidapptools.errors import SectionExistsError, SectionMissingError, ValueValidationError
from gidapptools.gid_config.conversion.entry_typus_item import EntryTypus
from pprint import pprint
import os
import re

from datetime import timedelta


def test_gid_ini_config_general(example_config_1: Path, example_spec_1: Path):
    config = GidIniConfig(config_file=example_config_1, spec_file=example_spec_1)
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
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "debug", "this", "folder", 'ENV', 'data_types'}
    gid_ini_config.add_section('a_new_section')
    assert len(gid_ini_config.config.all_sections) == 7
    assert config_changes == 1
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "debug", "this", "folder", "a_new_section", 'ENV', 'data_types'}

    gid_ini_config.add_section("this")
    with pytest.raises(SectionExistsError):
        gid_ini_config.add_section("this", existing_ok=False)
    gid_ini_config.remove_section("debug")
    assert gid_ini_config.get("this", "something") == "blah"
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "this", "folder", "a_new_section", 'ENV', 'data_types'}
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
    x = gid_ini_config.get('ENV', "PATH")
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
