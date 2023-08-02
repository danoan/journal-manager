from danoan.journal_manager.control import config, model, exceptions, utils

import argparse
from pathlib import Path
import shutil
from typing import Iterable


# -------------------- API --------------------


def remove(template_name: str):
    """
    Remove a template from the registered templates list.

    Args:
        template_name: Name of a registered template.
    """
    config_file = config.get_configuration_file()

    template_list_file = config.get_template_list_file()
    updated_template_list = []
    for entry in template_list_file.list_of_template_data:
        if entry.name != template_name:
            updated_template_list.append(entry)
        else:
            dir_to_remove = Path(entry.filepath)
            if dir_to_remove.parent.as_posix() == config_file.default_template_folder:
                shutil.rmtree(dir_to_remove)
            else:
                raise RuntimeError(
                    f"I've got an unexpected path to remove: {dir_to_remove.as_posix()}. Aborting!"
                )

    if len(updated_template_list) == len(template_list_file.list_of_template_data):
        raise exceptions.InvalidName()
    else:
        template_list_file.list_of_template_data = updated_template_list
        template_list_file.write(config.get_configuration_file().template_data_filepath)


def register(template_name: str, template_filepath: str):
    """
    Register a journal template.

    A minimal journal template is composed of a mkdocs.yml file with
    optional placeholders. For example

    site_name: {{journal.title}}
    theme: material

    The placeholders follow the jinja2 package syntax.
    Here is the list of available placeholders:

    - {{journal.title}}
    - {{journal.name}}
    - {{journal.location_folder}}
    - {{journal.active}}

    A journal template could have as many files as necessary
    and an arbitrary folder structure.

    The template should be given as a path to the folder that
    contains the files that define the template. These files
    will be copied for each instance of journal that make use
    of that template.

    Args:
        template_name: Name of the template to be registered.
        template_filepath: Path to the template file taken as model.
    """
    config_file = config.get_configuration_file()

    target_template_filepath = Path(config_file.default_template_folder).joinpath(template_name)
    target_template_filepath.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_filepath, target_template_filepath)

    template_data = model.JournalTemplate(
        template_name, target_template_filepath.expanduser().as_posix()
    )
    template_list_file = config.get_template_list_file()
    template_list_file.list_of_template_data.append(template_data)

    template_list_file.write(config.get_configuration_file().template_data_filepath)


def list_templates() -> Iterable[str]:
    """
    List registered templates.

    Returns:
        A string for each registered template in the format:
        "template_name:template_filepath"
    """
    template_list = config.get_template_list_file().list_of_template_data

    if len(template_list) == 0:
        raise exceptions.EmptyList()

    for entry in template_list:
        yield f"{entry.name}:{entry.filepath}"


# -------------------- CLI --------------------


def __remove_template__(template_name: str, **kwargs):
    utils.ensure_configuration_file_exists()
    try:
        remove(template_name)
    except exceptions.InvalidName:
        print(f"Template {template_name} was not found.")
    except RuntimeError as ex:
        print(ex.message)
        exit(1)


def __register_template__(template_name: str, template_filepath: str, **kwargs):
    utils.ensure_configuration_file_exists()
    register(template_name, template_filepath)


def __list_templates__(**kwargs):
    utils.ensure_configuration_file_exists()

    try:
        for entry in list_templates():
            print(entry)
    except exceptions.EmptyList:
        print("No template registered yet.")


def get_parser(subparser_action=None):
    command_name = "template"
    command_description = """
    Collection of commands to manage journal templates.

    If no subcommand is given, list the registered templates.
    """
    command_help = command_description

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            formatter_class=argparse.RawTextHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    subparsers = parser.add_subparsers()

    register_command_description = register.__doc__ if register.__doc__ else ""
    register_command_help = register_command_description.split(".")[0]

    register_subparser = subparsers.add_parser(
        "register",
        help=register_command_help,
        description=register_command_description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_subparser.add_argument("template_name", help="Template name")
    register_subparser.add_argument("template_filepath", help="Template filepath")
    register_subparser.set_defaults(func=__register_template__)

    remove_command_description = remove.__doc__ if remove.__doc__ else ""
    remove_command_help = remove_command_description.split(".")[0]

    remove_subparser = subparsers.add_parser(
        "remove",
        help=remove_command_help,
        description=remove_command_description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    remove_subparser.add_argument("template_name", help="Template name")
    remove_subparser.set_defaults(func=__remove_template__)

    parser.set_defaults(subcommand_help=parser.print_help, func=__list_templates__)

    return parser
