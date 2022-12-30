from danoan.journal_manager.control import model

from dataclasses import dataclass
import itertools
from pathlib import Path
import re
from typing import Iterable, Any


def peek_is_empty(iterable: Iterable[Any]):
    try:
        first = next(iterable)
    except StopIteration:
        return True, iterable
    return False, itertools.chain([first], iterable)


# -------------------- "Text Processing" --------------------
def journal_name_from_title(journal_title: str):
    return re.sub(r"[\s]+", "-", journal_title.lower().strip())


def journal_title_from_name(journal_name: str):
    return re.sub(r"-", " ", journal_name).capitalize()


def quick_notes_filename(journal_name: str):
    return f"{journal_name}-quick-notes.toml"


# -------------------- "Data Model Query" --------------------
def ensure_journal_name_is_unique(journal_data_file: model.JournalDataList, journal_name: str):
    for entry in journal_data_file.list_of_journal_data:
        if entry.name == journal_name:
            print(
                f"A journal with name {journal_name} is registered already. Please, choose a different name."
            )
            exit(1)


def find_template_by_name(template_file: model.JournalTemplateList, template_name: str):
    for entry in template_file:
        if entry.name == template_name:
            return entry
    return None


def find_journal_by_name(journal_data_file: model.JournalDataList, journal_name: str):
    for journal_data in journal_data_file.list_of_journal_data:
        if journal_data.name == journal_name:
            return journal_data

    return None


def find_journal_by_location(journal_data_file: model.JournalDataList, journal_location: str):
    for journal_data in journal_data_file.list_of_journal_data:
        if journal_data.location_folder == journal_location:
            return journal_data
    return None
