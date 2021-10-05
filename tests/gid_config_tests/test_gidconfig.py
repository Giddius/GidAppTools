import pytest
from pathlib import Path
from gidapptools.gid_config.interface import GidIniConfig
from gidapptools.errors import SectionExistsError, SectionMissingError
from pprint import pprint
import os


def test_gid_ini_config_general(example_config_1: Path, example_spec_1: Path):
    config = GidIniConfig(config_file=example_config_1, spec_file=example_spec_1)
    config.reload()

    assert config.as_dict() == {'debug': {'current_testing_channel': 'bot-testing'},
                                'folder': {'folder_1': Path('C:/Program Files/Git/cmd')},
                                'general_settings': {'cogs_location': 'antipetros_discordbot.cogs',
                                                     'guild_id': 449481990513754112,
                                                     'main_folder_name': 'antipetros_discordbot',
                                                     'owner_ids': [122348088319803392,
                                                                   346595708180103170,
                                                                   262095121527472128,
                                                                   225100859674066945]},
                                'this': {'something': 'blah', 'that': 40}}

    assert config.as_dict(raw=True) == {'debug': {'current_testing_channel': 'bot-testing'},
                                        'folder': {'folder_1': 'C:\\Program Files\\Git\\cmd'},
                                        'general_settings': {'cogs_location': 'antipetros_discordbot.cogs',
                                                             'guild_id': '449481990513754112',
                                                             'main_folder_name': 'antipetros_discordbot',
                                                             'owner_ids': '122348088319803392, 346595708180103170, '
                                                             '262095121527472128, 225100859674066945'},
                                        'this': {'something': 'blah', 'that': '40'}}
    config.reload()


def test_gid_ini_config_sections(gid_ini_config: GidIniConfig):
    config_changes = 0

    def config_has_changed(*args):
        nonlocal config_changes
        config_changes += 1
    gid_ini_config.reload()
    gid_ini_config.config.changed_signal.connect(config_has_changed)
    assert len(gid_ini_config.config.all_sections) == 5
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "debug", "this", "folder", 'ENV'}
    gid_ini_config.add_section('a_new_section')
    assert len(gid_ini_config.config.all_sections) == 6
    assert config_changes == 1
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "debug", "this", "folder", "a_new_section", 'ENV'}

    gid_ini_config.add_section("this")
    with pytest.raises(SectionExistsError):
        gid_ini_config.add_section("this", existing_ok=False)
    gid_ini_config.remove_section("debug")

    assert len(gid_ini_config.config.all_sections) == 5
    assert set(gid_ini_config.config.all_section_names) == {"general_settings", "this", "folder", "a_new_section", 'ENV'}
    assert config_changes == 2
    with pytest.raises(SectionMissingError):
        gid_ini_config.remove_section("debug", False)


def test_env_get(gid_ini_config: GidIniConfig):
    gid_ini_config.reload()
    x = gid_ini_config.get('ENV', "PATH")
    assert set(x) == {Path(item.strip()) for item in os.getenv('PATH').split(';') if item.strip()}
