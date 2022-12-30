from danoan.journal_manager.control import config
from danoan.journal_manager.control import model

import os
from pathlib import Path
from textwrap import dedent

ENV_JOURNAL_MANAGER_CONFIG_FOLDER = "JOURNAL_MANAGER_CONFIG_FOLDER"


def create_configuration_file(journal_folder_default):
    config.get_configuration_folder().mkdir(parents=True)
    config.get_template_folder().mkdir(parents=True)

    journal_data_filepath = (
        Path.expanduser(config.get_configuration_filepath().parent)
        .joinpath("journal_data.toml")
        .as_posix()
    )
    journal_template_data_filepath = (
        Path.expanduser(config.get_configuration_filepath().parent)
        .joinpath("template_data.toml")
        .as_posix()
    )

    parameters = model.Parameters()
    model.ConfigurationFile(
        journal_folder_default,
        journal_data_filepath,
        journal_template_data_filepath,
        parameters,
    ).write(config.get_configuration_filepath().as_posix())
    model.JournalDataList([]).write(journal_data_filepath)
    model.JournalTemplateList([]).write(journal_template_data_filepath)


def check_or_create_configuration_file():
    if not config.get_configuration_filepath().exists():
        config.get_configuration_folder().mkdir(parents=True)
        config.get_template_folder().mkdir(parents=True)
        print(
            dedent(
                f"""
                The configuration file is being created for the first time. 
                It is located at: {config.get_configuration_filepath()}.

                Please inform the requested values.
                """
            )
        )

        journal_folder_default = (
            Path(input("""Default location for created journals:""")).expanduser().as_posix()
        )

        create_configuration_file(journal_folder_default)
        return False
    else:
        return True


def get_configuration_folder():
    if ENV_JOURNAL_MANAGER_CONFIG_FOLDER not in os.environ:
        print(
            dedent(
                f"""
                There is no environment variable set for journal-manager.
                Create the environment variable {ENV_JOURNAL_MANAGER_CONFIG_FOLDER} and try again

                Example:
                export JOURNAL_MANAGER_CONFIG_FOLDER={Path.home().joinpath(".config","journal-manager")}
                """
            )
        )
        exit(1)

    return Path(os.environ[ENV_JOURNAL_MANAGER_CONFIG_FOLDER]).expanduser()


def get_configuration_filepath():
    return get_configuration_folder().joinpath("config.toml")


def get_configuration_file():
    if not get_configuration_filepath().exists():
        print(
            dedent(
                """
                The configuration file for journal-manager does not exist. 
                You can create one with the command: journal-manager init
                """
            )
        )
        exit(1)

    return model.ConfigurationFile.read(get_configuration_filepath())


def get_template_folder():
    return get_configuration_folder().joinpath("templates")


def get_quick_notes_folder():
    return get_configuration_folder().joinpath("quick-notes")


def get_template_list_file():
    config_file = get_configuration_file()
    return model.JournalTemplateList.read(config_file.template_data_filepath)


def get_journal_data_file() -> model.JournalDataList:
    config_file = get_configuration_file()
    return model.JournalDataList.read(config_file.journal_data_filepath)
