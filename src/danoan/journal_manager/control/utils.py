from danoan.journal_manager.control import model
from danoan.journal_manager.control import config

import itertools
from pathlib import Path
import re
from textwrap import dedent
from typing import Iterator, Any, Optional, Tuple


# -------------------- "Termination Criteria" --------------------
def ensure_configuration_folder_exists():
    """
    Exit application if configuration folder does not exist.
    """
    try:
        config.get_configuration_folder()
    except config.ConfigurationFileDoesNotExist:
        print(
            dedent(
                f"""
                    There is no environment variable set for journal-manager.
                    Create the environment variable {config.ENV_JOURNAL_MANAGER_CONFIG_FOLDER} and try again

                    Example:
                    export JOURNAL_MANAGER_CONFIG_FOLDER={Path.home().joinpath(".config","journal-manager")}
                    """
            )
        )
        exit(1)
    except Exception:
        print(f"Unexpected error while retrieving {config.ENV_JOURNAL_MANAGER_CONFIG_FOLDER}.")
        exit(1)


def ensure_configuration_file_exists():
    """
    Exit application if configuration file does not exist.
    """
    try:
        config.get_configuration_file()
    except config.ConfigurationFileDoesNotExist:
        print(
            dedent(
                """
                The configuration file for journal-manager does not exist. 
                You can create one with the command: journal-manager init
                """
            )
        )
        exit(1)
    except Exception:
        print("Unexpected error while retrieving the configuration file.")
        exit(1)


def ensure_journal_name_is_unique(journal_data_file: model.JournalDataList, journal_name: str):
    """
    Exit application if journal name exist already.
    """
    for entry in journal_data_file.list_of_journal_data:
        if entry.name == journal_name:
            print(
                f"A journal with name {journal_name} is registered already. Please, choose a different name."
            )
            exit(1)


def peek_is_empty(iterator: Iterator[Any]) -> Tuple[bool, Iterator[Any]]:
    """
    Check for emptiness of the first element without advancing the iterator.
    """
    try:
        first = next(iterator)
    except StopIteration:
        return True, iterator
    return False, itertools.chain([first], iterator)


# -------------------- "Text Processing" --------------------
def journal_name_from_title(journal_title: str) -> str:
    """
    Return a lower-snake-case version from a capitalized whitespace separated string.
    """
    return re.sub(r"[\s]+", "-", journal_title.lower().strip())


def journal_title_from_name(journal_name: str) -> str:
    """
    Return a capitalized whitespace separted from a lower-snake-case version of a string.
    """
    return re.sub(r"-", " ", journal_name).capitalize()


# -------------------- "Data Model Query" --------------------
def find_template_by_name(
    template_file: model.JournalTemplateList, template_name: str
) -> Optional[model.JournalTemplate]:
    """
    Search a registered template by name and return it.

    If the template is not found, a None object is returned.
    """
    for entry in template_file.list_of_template_data:
        if entry.name == template_name:
            return entry
    return None


def find_journal_by_name(
    journal_data_file: model.JournalDataList, journal_name: str
) -> Optional[model.JournalData]:
    """
    Search a registered journal by name and return it.

    If the journal is not found, a None object is returned.
    """
    for journal_data in journal_data_file.list_of_journal_data:
        if journal_data.name == journal_name:
            return journal_data

    return None


def find_journal_by_location(
    journal_data_file: model.JournalDataList, journal_location: str
) -> Optional[model.JournalData]:
    """
    Search a registered journal by location and return it.

    If the journal is not found, a None object is returned.
    """
    for journal_data in journal_data_file.list_of_journal_data:
        if journal_data.location_folder == journal_location:
            return journal_data
    return None
