from danoan.journal_manager.control import config

import argparse
from textwrap import dedent


def init(default_journal_folder: str = None, **kwargs):
    """
    Initialize journal-manager settings.

    This function creates the following files:

    - configuration file: Default directories and user preferences.
    - journal data file: Journal metadata.
    - template data file: Template metadata.

    The three files are created at the location stored in the
    environment variable JOURNAL_MANAGER_CONFIG_FOLDER.

    Args:
        default_journal_folder: Path to the default location where journals will be created.
        **kwargs: Any extra keyword argument is accepted, but ignored by the function.
    Returns:
        Nothing.
    """
    if config.get_configuration_filepath().exists():
        config_file_exists_already = True
        config_file = config.get_configuration_file()

        if default_journal_folder:
            config_file.default_journal_folder = default_journal_folder

        config_file.write(config.get_configuration_filepath())
    else:
        config.create_configuration_file(default_journal_folder)
        config_file_exists_already = False

    config_file = config.get_configuration_file()
    if config_file_exists_already:
        print(
            dedent(
                f"""
                  The configuration file exists already. 
                  It is located at: {config.get_configuration_filepath()} and here it is its content after the update:
                  default_journal_folder={config_file.default_journal_folder}
                  journal_data_filepath={config_file.journal_data_filepath}
                  template_data_filepath={config_file.template_data_filepath}
                  """
            )
        )


def get_parser(subparser_action=None):
    command_name = "init"
    command_description = init.__doc__
    command_help = init.__doc__.split(".")[0]

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
        "--default-journal-folder", help="Directory where journals will be created by default"
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=init)

    return parser
