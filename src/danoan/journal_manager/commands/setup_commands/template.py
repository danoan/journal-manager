from danoan.journal_manager.control import config, model, utils

import argparse
from pathlib import Path
import shutil


# -------------------- API --------------------


def remove(template_name: str):
    """
    Remove a template from the registered templates list.

    Args:
        template_name: Name of a registered template.
        **kwargs: Any extra keyword argument is accepted, but ignored by the function.
    Returns:
        Nothing.
    """
    config_file = config.get_configuration_file()

    template_list_file = config.get_template_list_file()
    updated_template_list = []
    for entry in template_list_file.list_of_template_data:
        if entry.name != template_name:
            updated_template_list.append(entry)
        else:
            dir_to_remove = Path(entry.filepath).parent
            if dir_to_remove.parent.as_posix() == config_file.default_template_folder:
                shutil.rmtree(dir_to_remove)
            else:
                print(
                    f"I've got an unexpected path to remove: {dir_to_remove.as_posix()}. Aborting!"
                )
                exit(1)

    if len(updated_template_list) == len(template_list_file.list_of_template_data):
        print(f"Template {template_name} was not found.")
    else:
        template_list_file.list_of_template_data = updated_template_list
        template_list_file.write(config.get_configuration_file().template_data_filepath)


def register(template_name: str, template_filepath: str):
    """
    Register a journal template.

    A journal template is a mkdocs.yml file with placeholders. For example

    site_name: {{journal.title}}
    theme: material

    The placeholders follow the jinja2 package syntax.
    Here is the list of available placeholders:

    - {{journal.title}}
    - {{journal.name}}
    - {{journal.location_folder}}
    - {{journal.active}}

    Args:
        template_name: Name of the template to be registered.
        template_filepath: Path to the template file taken as model.
    Returns:
        Nothing.
    """
    config_file = config.get_configuration_file()

    target_template_filepath = Path(config_file.default_template_folder).joinpath(
        template_name, "mkdocs.yml"
    )
    target_template_filepath.parent.mkdir(parents=True)
    shutil.copyfile(template_filepath, target_template_filepath)

    template_data = model.JournalTemplate(
        template_name, target_template_filepath.expanduser().as_posix()
    )
    template_list_file = config.get_template_list_file()
    template_list_file.list_of_template_data.append(template_data)

    template_list_file.write(config.get_configuration_file().template_data_filepath)


def list_templates():
    """
    List registered templates.

    Args:
        **kwargs: Any extra keyword argument is accepted, but ignored by the function.
    Returns:
        Nothing.
    """
    template_list = config.get_template_list_file().list_of_template_data

    if len(template_list) == 0:
        print("No template registered yet.")

    for entry in template_list:
        print(f"{entry.name}={entry.filepath}")


# -------------------- CLI --------------------


def __remove_template__(template_name: str, **kwargs):
    utils.ensure_configuration_file_exists()
    remove(template_name)


def __register_template__(template_name: str, template_filepath: str, **kwargs):
    utils.ensure_configuration_file_exists()
    register(template_name, template_filepath)


def __list_templates__(**kwargs):
    utils.ensure_configuration_file_exists()
    list_templates()


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
