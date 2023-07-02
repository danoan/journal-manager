from danoan.journal_manager.control.config import ENV_JOURNAL_MANAGER_CONFIG_FOLDER
from danoan.journal_manager.commands.setup_commands import init

import pytest


@pytest.fixture(scope="function")
def jm_config_folder_path(tmp_path):
    return tmp_path.joinpath("journal-manager")


@pytest.fixture(scope="function")
def f_set_env_variable(jm_config_folder_path, monkeypatch):
    monkeypatch.setenv(
        ENV_JOURNAL_MANAGER_CONFIG_FOLDER, jm_config_folder_path.expanduser().as_posix()
    )
    return {"journal_manager_config_folder": jm_config_folder_path}


@pytest.fixture(scope="function")
def f_setup_init(f_set_env_variable, tmp_path):
    default_journal_folder = tmp_path.joinpath("journals").expanduser()
    default_template_folder = tmp_path.joinpath("templates").expanduser()
    init.init_journal_manager(default_journal_folder, default_template_folder)
