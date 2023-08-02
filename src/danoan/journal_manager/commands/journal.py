from danoan.journal_manager.control import config, exceptions, utils
from danoan.journal_manager.commands.journal_commands import (
    activate,
    create,
    deactivate,
    deregister,
    edit,
    show,
    register,
)

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
    command_name = "journal"
    command_description = """
    Collection of commands to edit journals. 

    If no sub-command is given, list the registered journals.
    """
    command_help = command_description

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name, description=command_description, help=command_help, aliases=["j"]
        )
    else:
        parser = argparse.ArgumentParser(command_name, description=command_description)

    list_of_commands = [activate, create, deactivate, deregister, edit, show, register]

    subparser_action = parser.add_subparsers(title="Journal subcommands")
    for command in list_of_commands:
        command.get_parser(subparser_action)

    parser.set_defaults(subcommand_help=parser.print_help, func=__list_journals__)

    return parser
