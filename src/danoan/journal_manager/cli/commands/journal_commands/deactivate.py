from danoan.journal_manager.core import api, exceptions, model
from danoan.journal_manager.cli import utils

import argparse
from typing import List

# -------------------- API --------------------


def deactivate(journal_names: List[str]):
    """
    Deactivate a journal to be built.

    Args:
        journal_names: List of journal names in the register to deactivate.
    Raises:
        InvalidName if one or more journal names are not present in the list of registered journals.
    """
    config_file = api.get_configuration_file()
    journal_data_file = api.get_journal_data_file()

    updated_journal_data_list = []
    not_found_journal_names = []
    for journal_name in journal_names:
        journal = api.find_journal_by_name(journal_data_file, journal_name)
        if journal:
            journal.active = False
        else:
            not_found_journal_names.extend(journal_names)
        updated_journal_data_list.append(journal)

    if len(not_found_journal_names) > 0:
        raise exceptions.InvalidName(not_found_journal_names)

    journal_data_list = model.JournalDataList(updated_journal_data_list)

    with open(config_file.journal_data_filepath, "w") as f:
        journal_data_list.write(f)


# -------------------- CLI --------------------


def __deactivate__(journal_names: List[str], **kwargs):
    utils.ensure_configuration_file_exists()
    try:
        deactivate(journal_names)
    except exceptions.InvalidName as ex:
        print(
            f"The journals names: {ex.names} are not registered. Any deactivation was done."
        )


def get_parser(subparser_action=None):
    command_name = "deactivate"
    command_description = deactivate.__doc__ if deactivate.__doc__ else ""
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
        "journal_names",
        nargs="*",
        action="store",
        help="Names of journals to deactivate",
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=__deactivate__)

    return parser