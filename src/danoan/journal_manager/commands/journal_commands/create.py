from danoan.journal_manager.control import config, model, utils
from danoan.journal_manager.control.wrappers import mkdocs_wrapper

import argparse
from importlib_resources import files, as_file
from pathlib import Path
import shutil
from typing import Optional

from jinja2 import FileSystemLoader, Environment, Template, PackageLoader

# -------------------- API --------------------


def create_mkdocs_from_template(journal_data: model.JournalData, template: Template):
    journal_configuration_file = Path(journal_data.location_folder).joinpath("mkdocs.yml")
    journal_docs_folder = Path(journal_data.location_folder).joinpath("docs")
    journal_index = journal_docs_folder.joinpath("index.md")

    journal_docs_folder.mkdir()
    with open(journal_configuration_file, "w") as f:
        f.write(template.render({"journal": journal_data}))

    with open(journal_index, "w") as f:
        f.write(f"# {journal_data.title}")


def create_mkdocs_from_quick_notes_template(journal_data: model.JournalData):
    env = Environment(loader=PackageLoader("danoan.journal_manager", package_path="templates"))
    template = env.get_template(Path("").joinpath("quick-notes", "mkdocs.tpl.yaml").as_posix())

    create_mkdocs_from_template(journal_data, template)

    journal_docs_folder = Path(journal_data.location_folder).joinpath("docs")

    material_overrides = files("danoan.journal_manager.templates").joinpath(
        "quick-notes", "material-overrides"
    )
    with as_file(material_overrides) as material_overrides_path:
        shutil.copytree(
            material_overrides_path, Path(journal_data.location_folder).joinpath("overrides")
        )

    journal_quick_notes = journal_docs_folder.joinpath("quick-notes.md")
    journal_quick_notes.touch()


def create_mkdocs_from_template_name(journal_data: model.JournalData, template_name: str):
    config_file = config.get_configuration_file()

    journal_template_list = model.JournalTemplateList.read(config_file.template_data_filepath)

    template_entry = utils.find_template_by_name(journal_template_list, template_name)
    if not template_entry:
        print(
            f"The template {template_name} does not exist. Please enter an existent template name"
        )
        exit(1)

    env = Environment(loader=FileSystemLoader(config_file.default_template_folder))
    relative_path_to_template = Path(template_entry.filepath).relative_to(
        config_file.default_template_folder
    )
    template = env.get_template(str(relative_path_to_template))

    create_mkdocs_from_template(journal_data, template)


def create(
    journal_title: str,
    journal_location_folder: Path,
    mkdocs_template_name: Optional[str] = None,
):
    """
    Creates a mkdocs journal file structure.

    If the JOURNAL_LOCATION_FOLDER is not given, it uses the default_journal_folder defined
    in the file pointed by the JOURNAL_MANAGER_CONFIG_FOLDER environment variable is used.

    The MKDOCS_TEMPLATE_NAME specifies a template to create the mkdocs.yml file. To see a list
    of available templates, use:

    Example:
        journal-manager setup template

    Args:
        journal_title: Name will be displayed in the html page.
        journal_location_folder (optional): Directory where the journal files will be created
        mkdocs_template_name (optional): The name of a template file for mkdocs.yml
    Returns:
        Nothing
    """
    config_file = config.get_configuration_file()

    journal_name = utils.journal_name_from_title(journal_title)

    journal_data_file = model.JournalDataList.read(config_file.journal_data_filepath)
    utils.ensure_journal_name_is_unique(journal_data_file, journal_name)

    journal_location = journal_location_folder.joinpath(journal_name).expanduser()
    journal_location.mkdir(parents=True)

    journal_data = model.JournalData(journal_name, journal_location.as_posix(), True, journal_title)
    journal_data_file.list_of_journal_data.append(journal_data)

    if mkdocs_template_name:
        create_mkdocs_from_template_name(journal_data, mkdocs_template_name)
    else:
        create_mkdocs_from_quick_notes_template(journal_data)

    journal_data_file.write(config_file.journal_data_filepath)


# -------------------- CLI --------------------


def __create__(
    journal_title: str,
    journal_location_folder: Optional[Path] = None,
    mkdocs_template_name: Optional[str] = None,
    **kwargs,
):
    utils.ensure_configuration_file_exists()
    if journal_location_folder is None:
        journal_location_folder = config.get_configuration_file().default_journal_folder
    create(journal_title, journal_location_folder, mkdocs_template_name)


def get_parser(subparser_action=None):
    command_name = "create"
    command_description = create.__doc__ if create.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["c"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("journal_title", help="Journal title.")
    parser.add_argument(
        "--journal-folder",
        dest="journal_location_folder",
        help=f"Location where the journal folder will be stored. If empty, the default location is chosen.",
        type=Path,
    )
    parser.add_argument(
        "--template-name",
        dest="mkdocs_template_name",
        help="Template for a mkdocs configuration file. Templates are registered via the setup subcommand.",
    )

    parser.set_defaults(subcommand_help=parser.print_help, func=__create__)

    return parser
