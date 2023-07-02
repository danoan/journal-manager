from danoan.journal_manager.control import config, model, utils

import argparse
from typing import List, Optional


# -------------------- API --------------------


def show(journal_name: str, attribute_names: List[str], **kwargs):
    """
    Show information about a journal.

    Args:
        journal_name: The journal name
        attribute_names (optional): List of attribute names which values one wants to show
    Returns:
        Nothing
    """
    journal_data_list = config.get_journal_data_file().list_of_journal_data

    for journal in journal_data_list:
        if journal.name == journal_name:
            if len(attribute_names) == 0:
                attribute_names = list(journal.__dict__.keys())

            for name in attribute_names:
                print(f"{name}: {journal.__dict__[name]}")
            break


# -------------------- CLI --------------------


def __show__(journal_name: str, attribute_names: Optional[List[str]] = None, **kwargs):
    utils.ensure_configuration_file_exists()
    if not attribute_names:
        attribute_names = []

    # The action 'append' adds a None object if nothing is passed (assuming nargs='?')
    if len(attribute_names) > 0 and attribute_names[0] is None:
        attribute_names.remove(None)

    show(journal_name, attribute_names)


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
    parser.set_defaults(subcommand_help=parser.print_help, func=__show__)

    return parser
