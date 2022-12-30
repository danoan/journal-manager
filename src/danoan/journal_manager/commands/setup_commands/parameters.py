from danoan.journal_manager.control import config

import argparse
from pathlib import Path


def set_parameters(editor: str = None, **kwargs):
    """
    Set the parameter's values passed as arguments.

    Args:
        editor: Path to the default text editor to use.
        **kwargs: Any extra keyword argument is accepted, but ignored by the function.
    Returns:
        Nothing.
    """
    config_file = config.get_configuration_file()

    if editor:
        config_file.parameters.default_text_editor_path = Path(editor).expanduser().as_posix()

    config_file.write(config.get_configuration_filepath())


def list_or_set(**kwargs):
    """
    List or set parameters.

    This function will list the parameters available if no argument is given.
    If arguments are given, it will set the correspondent parameter.

    Args:
        **kwargs: Any keyword argument type is accepted, but it will be ignored if the
        keyword is not a subcommand parameter.
    Returns:
        Nothing.
    """
    parameter_list = ["editor"]
    if any([p in kwargs.keys() and kwargs[p] for p in parameter_list]):
        set_parameters(**kwargs)
    else:
        config_file = config.get_configuration_file()
        print(f"default_text_editor_path: {config_file.parameters.default_text_editor_path}")


def get_parser(subparser_action=None):
    command_name = "parameters"
    command_description = list_or_set.__doc__
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            help=command_help,
            description=command_description,
            formatter_class=argparse.RawTextHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument(
        "--editor", help="Path to the default text editor to use when editing files."
    )

    parser.set_defaults(subcommand_help=parser.print_help, func=list_or_set)

    return parser
