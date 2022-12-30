from danoan.journal_manager.control import config

import argparse


def list(**kwargs):
    """
    List registered journals.
    """
    list_of_journal_data = config.get_journal_data_file().list_of_journal_data

    if len(list_of_journal_data) == 0:
        print("There is no journal registered yet.")
        return

    for entry in list_of_journal_data:
        print(f"{entry.name}: {entry.location_folder}")


def get_parser(subparser_action=None):
    command_name = "list"
    command_description = list.__doc__
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

    parser.set_defaults(subcommand_help=parser.print_help, func=list)

    return parser
