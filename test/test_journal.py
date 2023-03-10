from danoan.journal_manager.commands import journal_commands as jm
from danoan.journal_manager.control import config

from danoan.journal_manager.commands.setup_commands.template import register as register_template

import argparse
from conftest import *
from pathlib import Path
import pytest


class TestRegister:
    def test_register_deregister_journal(self, f_setup_init, tmp_path):
        # Register
        first_location_folder = tmp_path.joinpath("first-journal").expanduser().as_posix()
        first_journal_title = "My First Journal Title"
        jm.register.register(first_location_folder, first_journal_title)

        journal_data = config.get_journal_data_file().list_of_journal_data[0]

        assert journal_data.name == "my-first-journal-title"
        assert journal_data.title == first_journal_title
        assert journal_data.location_folder == first_location_folder
        assert journal_data.active == True

        # Register a second one
        second_location_folder = tmp_path.joinpath("second-journal").expanduser().as_posix()
        second_journal_title = "My Second Journal Title"
        jm.register.register(second_location_folder, second_journal_title)

        list_of_journal_data = config.get_journal_data_file().list_of_journal_data
        assert len(list_of_journal_data) == 2

        # Deregister
        jm.deregister.deregister("my-first-journal-title")

        list_of_journal_data = config.get_journal_data_file().list_of_journal_data
        assert len(list_of_journal_data) == 1

        journal_data = config.get_journal_data_file().list_of_journal_data[0]

        assert journal_data.name == "my-second-journal-title"
        assert journal_data.title == second_journal_title
        assert journal_data.location_folder == second_location_folder
        assert journal_data.active == True


class TestActivate:
    def test_activate_deactivate_journal(self, f_setup_init, tmp_path):
        journal_title = "My Journal Title"
        jm.register.register(tmp_path, journal_title)

        journal_data = config.get_journal_data_file().list_of_journal_data[0]
        assert journal_data.title == journal_title
        assert journal_data.active == True

        # Deactivate
        jm.deactivate.deactivate([journal_data.name])
        journal_data = config.get_journal_data_file().list_of_journal_data[0]

        assert journal_data.title == journal_title
        assert journal_data.active == False

        # Activate

        jm.activate.activate([journal_data.name])
        journal_data = config.get_journal_data_file().list_of_journal_data[0]

        assert journal_data.title == journal_title
        assert journal_data.active == True


class TestCreate:
    @pytest.mark.parametrize(
        "journal_location_folder_str, template_name",
        [(None, None), ("journals-repository", "research")],
    )
    def test_create_journal(
        self, f_setup_init, tmp_path, journal_location_folder_str, template_name
    ):
        journal_title = "My Journal Title"
        template_filepath = tmp_path.joinpath("my-template.yml")
        template_filepath.touch()
        register_template("research", template_filepath.expanduser().as_posix())

        journal_location_folder = None
        if journal_location_folder_str:
            journal_location_folder = (
                tmp_path.joinpath(journal_location_folder_str).expanduser().as_posix()
            )

        jm.create.create(journal_title, journal_location_folder, template_name)

        # Intentionally put after create_journal such that the latter can be called
        # with a None object
        if not journal_location_folder:
            journal_location_folder = config.get_configuration_file().default_journal_folder

        journal_data = config.get_journal_data_file().list_of_journal_data[0]
        assert journal_data.title == journal_title
        assert (
            journal_data.location_folder
            == Path(journal_location_folder).joinpath("my-journal-title").expanduser().as_posix()
        )
        assert journal_data.active == True


class TestList:
    def test_list_journals_when_registry_is_empty(self, f_setup_init, capfd):
        jm.list.list()
        captured = capfd.readouterr()
        assert captured.out == "There is no journal registered yet.\n"

    def test_list_journals(self, f_setup_init, capfd):
        journal_title = "My Journal Title"

        jm.create.create(journal_title)
        journal_data = config.get_journal_data_file().list_of_journal_data[0]

        jm.list.list()
        captured = capfd.readouterr()
        assert captured.out == f"{journal_data.name}: {journal_data.location_folder}\n"
