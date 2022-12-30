#! /usr/bin/env python3

import argparse
import sys

from danoan.journal_manager.commands import build, journal, setup


def get_parser():
    parser = argparse.ArgumentParser(description="Manager application for mkdocs journals")

    list_of_commands = [build, journal, setup]

    subparser_action = parser.add_subparsers(title="journal-manager subcommands")
    for command in list_of_commands:
        command.get_parser(subparser_action)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if "func" in args:
        args.func(**vars(args))
    else:
        if "subcommand_help" in args:
            args.subcommand_help()
        else:
            parser.print_help(sys.stdout)


if __name__ == "__main__":
    main()
