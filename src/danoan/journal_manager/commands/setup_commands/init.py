from danoan.journal_manager.control import config
from danoan.journal_manager.control import utils

import argparse
from pathlib import Path
from textwrap import dedent


# -------------------- API --------------------


def init_journal_manager(default_journal_folder: Path, default_template_folder: Path):
    """
    Initialize journal-manager settings.

    This sets up configuration values of journal-manager.

    Args:
        default_journal_folder: Path to the default location where journals will be created.
        default_template_folder: Path to the default location where journal templates will be stored.
    """
    config_file = config.get_configuration_file()

    config_file.default_journal_folder = default_journal_folder.as_posix()
    config_file.default_template_folder = default_template_folder.as_posix()

    config_file.write(config.get_configuration_filepath())


# -------------------- CLI --------------------


def __init_journal_manager__(default_journal_folder: Path, default_template_folder: Path, **kwargs):
    utils.ensure_configuration_folder_exists()

    config_file_exists_already = True
    try:
        config_file = config.get_configuration_file()
    except config.ConfigurationFileDoesNotExist:
        config.create_configuration_file(default_journal_folder, default_template_folder)
        config_file_exists_already = False

    init_journal_manager(default_journal_folder, default_template_folder)
    config_file = config.get_configuration_file()

    if config_file_exists_already:
        print(
            dedent(
                f"""
                  The configuration file exists already. 
                  It is located at: {config.get_configuration_filepath()} and here it is its content after the update:
                  default_journal_folder={config_file.default_journal_folder}
                  default_template_folder={config_file.default_template_folder}
                  journal_data_filepath={config_file.journal_data_filepath}
                  template_data_filepath={config_file.template_data_filepath}
                  """
            )
        )


def get_parser(subparser_action=None):
    command_name = "init"
    command_description = init_journal_manager.__doc__ if init_journal_manager.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            formatter_class=argparse.RawTextHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument(
        "--default-journal-folder",
        type=Path,
        help="Directory where journals will be created by default",
        default=config.get_configuration_folder().joinpath("journals"),
    )
    parser.add_argument(
        "--default-template-folder",
        type=Path,
        help="Directory where journals will be created by default",
        default=config.get_configuration_folder().joinpath("templates"),
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=__init_journal_manager__)

    return parser
