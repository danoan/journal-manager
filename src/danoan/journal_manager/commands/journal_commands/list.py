from danoan.journal_manager.control import config, exceptions, utils

import argparse


# -------------------- API --------------------


def list_journals():
    """
    List registered journals.

    Returns:
        A string for each registered journal in the format:
        "journal_name:location_folder".
    Raises:
        EmptyList if the journal register is empty.
    """
    list_of_journal_data = config.get_journal_data_file().list_of_journal_data

    if len(list_of_journal_data) == 0:
        raise exceptions.EmptyList()

    for entry in list_of_journal_data:
        yield f"{entry.name}:{entry.location_folder}"


# -------------------- CLI --------------------


def __list_journals__(**kwargs):
    utils.ensure_configuration_file_exists()

    try:
        for journal_list_entry in list_journals():
            print(journal_list_entry)
    except exceptions.EmptyList:
        print("There is no journal registered yet.")


def get_parser(subparser_action=None):
    command_name = "list"
    command_description = list.__doc__ if list.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            help=command_help,
            description=command_description,
            aliases=["l"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.set_defaults(subcommand_help=parser.print_help, func=__list_journals__)

    return parser
