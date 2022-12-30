from danoan.journal_manager.control import config

import argparse
from typing import List


def deregister(journal_names: List[str], **kwargs):
    """
    Deregister a journal from the list of registered journals.

    This function does not remove any file.
    """
    journal_data_file = config.get_journal_data_file()

    updated_list_of_journal_data = []

    for entry in journal_data_file.list_of_journal_data:
        if entry.name not in journal_names:
            updated_list_of_journal_data.append(entry)

    if len(updated_list_of_journal_data) == len(journal_data_file.list_of_journal_data):
        print(
            f"No registry was found for journals {', '.join(journal_names)}. Nothing was removed."
        )
    else:
        journal_data_file.list_of_journal_data = updated_list_of_journal_data
        journal_data_file.write(config.get_configuration_file().journal_data_filepath)


def get_parser(subparser_action=None):
    command_name = "deregister"
    command_description = deregister.__doc__
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["d"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument(
        "journal_names",
        action="extend",
        nargs="+",
        help="Name of the journal to be deregistered",
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=deregister)

    return parser
