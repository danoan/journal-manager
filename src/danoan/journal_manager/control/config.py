from danoan.journal_manager.control import config
from danoan.journal_manager.control import model

import os
from pathlib import Path
from textwrap import dedent

ENV_JOURNAL_MANAGER_CONFIG_FOLDER = "JOURNAL_MANAGER_CONFIG_FOLDER"


class ConfigurationFileDoesNotExist(BaseException):
    pass


class ConfigurationFolderDoesNotExist(BaseException):
    pass


def get_configuration_folder() -> Path:
    """
    Return the value contained in environment variable JOURNAL_MANAGER_CONFIG_FOLDER

    If the environment variable is not set, a message with instructions on how to set
    is displayed.
    """
    if ENV_JOURNAL_MANAGER_CONFIG_FOLDER not in os.environ:
        raise ConfigurationFolderDoesNotExist()

    return Path(os.environ[ENV_JOURNAL_MANAGER_CONFIG_FOLDER]).expanduser()


def get_configuration_filepath():
    return get_configuration_folder().joinpath("config.toml")


def get_configuration_file() -> model.ConfigurationFile:
    """
    Return a python dataclass representation of the journal-manager configuration file.

    If the file does not exist, an error message is printed and the program exits.
    """
    if not get_configuration_filepath().exists():
        raise ConfigurationFileDoesNotExist()

    return model.ConfigurationFile.read(get_configuration_filepath())


def get_template_list_file() -> model.JournalTemplateList:
    """
    Return a dataclass representation of the list of journal templates register file.
    """
    config_file = get_configuration_file()
    return model.JournalTemplateList.read(config_file.template_data_filepath)


def get_journal_data_file() -> model.JournalDataList:
    """
    Return a dataclass representation of the list of journals register file.
    """
    config_file = get_configuration_file()
    return model.JournalDataList.read(config_file.journal_data_filepath)


def create_configuration_file(journal_folder_default: Path, templates_folder_default: Path):
    """
    Create journal-manager application configuration file.

    Additionally, it creates two more configuration files:
        - journal_data.toml
        - template_data.toml

    and a folder to store journal templates.

    Args:
        journal_folder_default: Default location to store journals.
        templates_folder_default: Default location to store journal templates.
    Returns:
        Nothing.
    """
    config.get_configuration_folder().mkdir(parents=True)
    journal_folder_default.mkdir(parents=True)
    templates_folder_default.mkdir(parents=True)

    journal_data_filepath = (
        Path.expanduser(config.get_configuration_folder()).joinpath("journal_data.toml").as_posix()
    )
    journal_template_data_filepath = (
        Path.expanduser(config.get_configuration_folder()).joinpath("template_data.toml").as_posix()
    )

    parameters = model.Parameters()
    model.ConfigurationFile(
        journal_folder_default.as_posix(),
        templates_folder_default.as_posix(),
        journal_data_filepath,
        journal_template_data_filepath,
        parameters,
    ).write(get_configuration_filepath().as_posix())
    model.JournalDataList([]).write(journal_data_filepath)
    model.JournalTemplateList([]).write(journal_template_data_filepath)
