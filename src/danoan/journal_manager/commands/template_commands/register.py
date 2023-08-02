from danoan.journal_manager.control import config, model, utils

import argparse
from pathlib import Path
import shutil


# -------------------- API --------------------


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
        template_path: Path to a directory containing the template files.
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


# -------------------- CLI --------------------


def __register_template__(template_name: str, template_filepath: str, **kwargs):
    utils.ensure_configuration_file_exists()
    register(template_name, template_filepath)


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
            formatter_class=argparse.RawTextHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.set_defaults(func=__register_template__)

    return parser
