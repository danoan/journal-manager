from danoan.journal_manager.control import config, model, utils

import argparse
from pathlib import Path
from typing import Optional


def register(location_folder: Path, journal_title: Optional[str] = None):
    """
    Register an existing journal structure to the list of managed journals.

    If a journal_title is not specified, a title will be derived from
    the location_folder. A journal name is created from the journal_title
    by taking its `kebab-notation`.

    E.g.

    journal_title: My Journal Title
    journal_name: my-journal-title

    Args:
        location_folder: Directory where the journal files are located
        journal_title (optional): Journal title.
    Returns:
        Nothing
    """
    journal_data_file = config.get_journal_data_file()

    if journal_title is None:
        journal_title = Path(location_folder).expanduser().name

    journal_name = utils.journal_name_from_title(journal_title)
    utils.ensure_journal_name_is_unique(journal_data_file, journal_name)

    journal_data = model.JournalData(journal_name, location_folder.as_posix(), True, journal_title)
    journal_data_file.list_of_journal_data.append(journal_data)

    journal_data_file.write(config.get_configuration_file().journal_data_filepath)


def get_parser(subparser_action=None):
    command_name = "register"
    command_description = register.__doc__ if register.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["r"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("location_folder", help="Journal location folder")
    parser.add_argument("--title", dest="journal_title", help="Journal title")

    parser.set_defaults(subcommand_print=parser.print_help, func=register)

    return parser
