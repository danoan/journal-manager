from danoan.journal_manager.control import config, model

import argparse
from typing import List


def show(journal_name: str, attribute_names: List[str] = [], **kwargs):
    """
    Show information about a journal.

    Args:
        journal_name: The journal name
        attribute_names (optional): List of attribute names which values one wants to show
    Returns:
        Nothing
    """
    journal_data_list = config.get_journal_data_file().list_of_journal_data

    # The action 'append' adds a None object if nothing is passed (assuming nargs='?')
    if len(attribute_names) > 0 and attribute_names[0] is None:
        user_input_is_not_empty = False
        attribute_names.remove(None)
    else:
        user_input_is_not_empty = True

    for journal in journal_data_list:
        if journal.name == journal_name:
            if len(attribute_names) == 0:
                attribute_names = journal.__dict__.keys()

            if len(attribute_names) == 1 and user_input_is_not_empty:
                print(journal.__dict__[attribute_names[0]])
            else:
                for name in attribute_names:
                    print(f"{name}: {journal.__dict__[name]}")
                break


def get_parser(subparser_action=None):
    command_name = "show"
    command_description = show.__doc__ if show.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("journal_name", help="A registered journal name")
    parser.add_argument(
        "attribute_names",
        nargs="?",
        action="append",
        help="Attribute name which value one wants to show.",
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=show)

    return parser
