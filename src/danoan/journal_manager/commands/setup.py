from danoan.journal_manager.commands.setup_commands import init, template, parameters

import argparse


def get_parser(subparser_action=None):
    command_name = "setup"
    command_description = "Configure journal-manager settings."
    command_help = command_description

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name, description=command_description, help=command_help, aliases=["s"]
        )
    else:
        parser = argparse.ArgumentParser(command_name, description=command_description)

    list_of_commands = [init, template, parameters]

    subparser_action = parser.add_subparsers(title="Setup subcommands")
    for command in list_of_commands:
        command.get_parser(subparser_action)

    parser.set_defaults(subcommand_help=parser.print_help)

    return parser
