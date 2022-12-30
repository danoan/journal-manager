from danoan.journal_manager.commands.journal_commands import (
    activate,
    create,
    deactivate,
    deregister,
    edit,
    list,
    show,
    register,
)

import argparse


def get_parser(subparser_action=None):
    command_name = "journal"
    command_description = "Execute tasks involving journals"
    command_help = command_description

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name, description=command_description, help=command_help, aliases=["j"]
        )
    else:
        parser = argparse.ArgumentParser(
            command_name, description=command_description, help=command_help
        )

    list_of_commands = [activate, create, deactivate, deregister, edit, list, show, register]

    subparser_action = parser.add_subparsers(title="Journal subcommands")
    for command in list_of_commands:
        command.get_parser(subparser_action)

    parser.set_defaults(subcommand_help=parser.print_help)

    return parser
