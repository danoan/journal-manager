from danoan.journal_manager.control import config, exceptions, utils

import argparse
from pathlib import Path
import shutil


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


def get_parser(subparser_action=None):
    command_name = "remove"
    command_description = remove.__doc__ if remove.__doc__ else ""
    command_help = command_description.split(".")[0]

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

    parser.add_argument("template_name", help="Template name")
    parser.set_defaults(func=__remove_template__)

    return parser
