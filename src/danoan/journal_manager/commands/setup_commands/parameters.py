from danoan.journal_manager.control import config, utils

import argparse
from pathlib import Path
from typing import Optional, Iterable


# -------------------- API --------------------


def set_parameters(editor: Optional[Path]):
    """
    Set the parameter's values passed as arguments.

    Args:
        editor: Path to the default text editor to use.
    """
    config_file = config.get_configuration_file()

    if editor:
        config_file.parameters.default_text_editor_path = editor.expanduser().as_posix()

    config_file.write(config.get_configuration_filepath())


def list_parameters() -> Iterable[str]:
    """
    List parameters.

    This function will list the parameters available to configure a journal
    if no argument is given. If arguments are given, it will set the
    correspondent parameter.

    Returns:
        One string for each attribute in the format:
        "attribute_name: attribute_value"
    """
    config_file = config.get_configuration_file()
    for attr_name, _ in config_file.parameters.__dataclass_fields__.items():
        yield f"{attr_name}: {getattr(config_file.parameters,attr_name)}"


# -------------------- CLI --------------------


def __list_or_set__(**kwargs):
    """
    List or set parameters.
    """
    utils.ensure_configuration_file_exists()

    accepted_parameter_list = ["editor"]
    active_parameters = dict(
        list(filter(lambda x: x[0] in accepted_parameter_list, kwargs.items()))
    )
    if len(active_parameters) > 0:
        set_parameters(**active_parameters)
    else:
        list_parameters()


def get_parser(subparser_action=None):
    command_name = "parameters"
    command_description = __list_or_set__.__doc__ if __list_or_set__.__doc__ else ""
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
        "--editor", help="Path to the default text editor to use when editing files.",
        type=Path
    )

    parser.set_defaults(subcommand_help=parser.print_help, func=__list_or_set__)

    return parser
