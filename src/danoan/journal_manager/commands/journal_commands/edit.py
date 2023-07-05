from danoan.journal_manager.control import config, exceptions, utils
from danoan.journal_manager.control.wrappers import nvim_wrapper

import argparse
from pathlib import Path


# -------------------- API --------------------


def edit(journal_name: str):
    """
    Edit journal files.

    Opens the mkdocs.yml file for edition using the default editor specified
    in the file pointed by JOURNAL_MANAGER_CONFIG_FOLDER.

    Args:
        journal_name: The name of a journal in the registry.

    Raises:
        NotImplementedError if the requested editor application is not supported.
        InvalidName if the journal name is not registered.
    """
    journal_data_list = config.get_journal_data_file().list_of_journal_data

    config_file = config.get_configuration_file()
    text_editor_path = Path(config_file.parameters.default_text_editor_path)

    if not Path(text_editor_path).name.startswith("vim") and not Path(
        text_editor_path
    ).name.startswith("nvim"):
        raise NotImplementedError(
            message="This application only knows how to start vim or nvim editors."
        )

    for entry in journal_data_list:
        if entry.name == journal_name:
            mkdocs_config_path = Path(entry.location_folder).joinpath("mkdocs.yml")
            nvim_wrapper.edit_file(mkdocs_config_path.expanduser(), text_editor_path)
            return

    raise exceptions.InvalidName()


# -------------------- CLI --------------------


def __edit__(journal_name: str, **kwargs):
    utils.ensure_configuration_file_exists()
    try:
        edit(journal_name)
    except NotImplementedError as ex:
        print(ex.message)
        exit(1)
    except exceptions.InvalidName:
        print(f"Journal {journal_name} does not exist. Please enter an existent journal name.")


def get_parser(subparser_action=None):
    command_name = "edit"
    command_description = edit.__doc__ if edit.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            help=command_help,
            description=command_description,
            aliases=["e"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("journal_name", help="Journal name")
    parser.set_defaults(subcommand_help=parser.print_help, func=__edit__)

    return parser
