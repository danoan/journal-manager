from danoan.journal_manager.commands.setup_commands import init, parameters, template

from danoan.journal_manager.control import config

from conftest import *
from pathlib import Path
import pytest


# -------------------- Fixtures --------------------
@pytest.fixture(scope="function")
def f_unset_env_variable(monkeypatch):
    monkeypatch.delenv(config.ENV_JOURNAL_MANAGER_CONFIG_FOLDER, raising=False)


# -------------------- Tests --------------------
class TestInit:
    def test_no_environment_variable_set(self, f_unset_env_variable, tmp_path):
        with pytest.raises(config.ConfigurationFolderDoesNotExist) as e:
            default_journal_folder = tmp_path.joinpath("journals").expanduser()
            default_template_folder = tmp_path.joinpath("templates").expanduser()
            init.init(default_journal_folder, default_template_folder)

        assert e.type == config.ConfigurationFolderDoesNotExist

    def test_no_configuration_file_exist(self, f_set_env_variable, tmp_path):
        journal_manager_config_folder = f_set_env_variable["journal_manager_config_folder"]
        default_journal_folder = tmp_path.joinpath("journals").expanduser()
        default_template_folder = tmp_path.joinpath("templates").expanduser()
        init.init(default_journal_folder, default_template_folder)

        config_file = config.get_configuration_file()

        expected_journal_data_filepath = (
            journal_manager_config_folder.joinpath("journal_data.toml").expanduser()
        )
        expected_template_data_filepath = (
            journal_manager_config_folder.joinpath("template_data.toml").expanduser()
        )

        assert config_file.default_journal_folder == default_journal_folder.as_posix()
        assert config_file.journal_data_filepath == expected_journal_data_filepath.as_posix()
        assert config_file.template_data_filepath == expected_template_data_filepath.as_posix()
        assert config_file.parameters.default_text_editor_path == ""

    def test_configuration_file_exist(self, f_set_env_variable, tmp_path):
        first_default_journal_folder = tmp_path.joinpath("journals").expanduser()
        first_default_template_folder = tmp_path.joinpath("templates").expanduser()
        config.create_configuration_file(
            first_default_journal_folder, first_default_template_folder
        )

        config_file = config.get_configuration_file()
        assert config_file.default_journal_folder == first_default_journal_folder.as_posix()

        second_default_journal_folder = (
            tmp_path.joinpath("journals_another_path").expanduser()
        )
        second_default_template_folder = (
            tmp_path.joinpath("templates_another_path").expanduser()
        )
        init.init(second_default_journal_folder, second_default_template_folder)
        config_file = config.get_configuration_file()

        assert config_file.default_journal_folder == second_default_journal_folder.as_posix()
        assert config_file.default_template_folder == second_default_template_folder.as_posix()


class TestParameters:
    def test_editor_path(self, f_setup_init, tmp_path):
        config_file = config.get_configuration_file()
        assert config_file.parameters.default_text_editor_path == ""

        e_editor_path = tmp_path.joinpath("my-editor").expanduser()
        parameters.set_parameters(editor=e_editor_path)
        assert config_file.parameters.default_text_editor_path == ""


class TestTemplate:
    def test_template_register(self, f_setup_init, tmp_path):
        config_file = config.get_configuration_file()

        template_list_file = config.get_template_list_file()
        assert len(template_list_file.list_of_template_data) == 0

        template_filepath = tmp_path.joinpath("mkdocs.yml")
        template_filepath.touch()

        e_template_name = "my-new-template"
        e_template_filepath = (
            Path(config_file.default_template_folder)
            .joinpath(e_template_name, "mkdocs.yml")
            .expanduser()
            .as_posix()
        )

        template.register(e_template_name, template_filepath)
        template_list_file = config.get_template_list_file()
        assert len(template_list_file.list_of_template_data) == 1
        assert template_list_file.list_of_template_data[0].name == e_template_name
        assert template_list_file.list_of_template_data[0].filepath == e_template_filepath

    def test_template_remove(self, f_setup_init, tmp_path):
        self.test_template_register(f_setup_init, tmp_path)

        template_list_file = config.get_template_list_file()
        assert len(template_list_file.list_of_template_data) == 1

        template.remove("my-new-template")
        template_list_file = config.get_template_list_file()
        assert len(template_list_file.list_of_template_data) == 0
