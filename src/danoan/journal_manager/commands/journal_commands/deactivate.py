from danoan.journal_manager.control import config, model

import argparse
from typing import List


def deactivate(journal_names: List[str], **kwargs):
    """
    Deactivate a journal to be built.
    """
    config_file = config.get_configuration_file()
    journal_data_list = config.get_journal_data_file().list_of_journal_data

    updated_journal_data_list = []
    for journal in journal_data_list:
        for journal_name in journal_names:
            if journal.name == journal_name:
                journal.active = False
                break
        updated_journal_data_list.append(journal)

    journal_data_list = model.JournalDataList(updated_journal_data_list)
    journal_data_list.write(config_file.journal_data_filepath)


def get_parser(subparser_action=None):
    command_name = "deactivate"
    command_description = deactivate.__doc__
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            help=command_help,
            description=command_description,
            aliases=["dct"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument(
        "journal_names", nargs="*", action="store", help="Names of journals to deactivate"
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=deactivate)

    return parser
