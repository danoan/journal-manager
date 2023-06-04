from danoan.journal_manager.commands import journal_commands as jm
from danoan.journal_manager.commands.journal import get_parser as journal_parser
from danoan.journal_manager.commands import build
from danoan.journal_manager.commands import setup_commands as setup
from danoan.journal_manager.commands.setup import get_parser as setup_parser
from danoan.journal_manager.control import config

import argparse
from conftest import *
import pytest


@pytest.fixture(scope="function")
def f_unset_env_variable(monkeypatch):
    monkeypatch.delenv(config.ENV_JOURNAL_MANAGER_CONFIG_FOLDER, raising=False)


@pytest.mark.usefixtures("f_set_env_variable")
class TestParser:
    def parser_tester(self, get_parser_function):
        assert not get_parser_function().prog.startswith("test-command")

        subparser_action = argparse.ArgumentParser("test-command").add_subparsers()
        assert get_parser_function(subparser_action).prog.startswith("test-command")


@pytest.mark.usefixtures("f_setup_init")
class TestJournalParsers(TestParser):
    def test_journal_parser(self):
        self.parser_tester(journal_parser)

    def test_activate_parser(self):
        self.parser_tester(jm.activate.get_parser)

    def test_create_parser(self):
        self.parser_tester(jm.create.get_parser)

    def test_deactivate_parser(self):
        self.parser_tester(jm.deactivate.get_parser)

    def test_deregister_parser(self):
        self.parser_tester(jm.deregister.get_parser)

    def test_edit_parser(self):
        self.parser_tester(jm.edit.get_parser)

    def test_list_parser(self):
        self.parser_tester(jm.list.get_parser)

    def test_register_parser(self):
        self.parser_tester(jm.register.get_parser)


# class TestJournalParsersWithoutInitialization(TestParser):
#     def test_journal_parser(self):
#         with pytest.raises(SystemExit) as e:
#             self.parser_tester(journal_parser)

#         assert e.type == SystemExit
#         assert e.value.code == 1


class TestBuildParser(TestParser):
    # def test_build_parser_without_initialization(self):
    #     with pytest.raises(SystemExit) as e:
    #         self.parser_tester(build.get_parser)

    #     assert e.type == SystemExit
    #     assert e.value.code == 1

    def test_build_parser_with_initialization(self, f_setup_init):
        self.parser_tester(build.get_parser)


class TestSetupParser(TestParser):
    def test_setup_parser(self):
        self.parser_tester(setup_parser)

    def test_init_parser(self):
        self.parser_tester(setup.init.get_parser)

    def test_parameters_parser(self):
        self.parser_tester(setup.parameters.get_parser)

    def test_template_parser(self):
        self.parser_tester(setup.template.get_parser)
