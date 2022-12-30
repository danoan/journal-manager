from danoan.journal_manager.commands.build import build as build_journal
import danoan.journal_manager.commands.journal_commands as jm

from danoan.journal_manager.control import config
from danoan.journal_manager.control import model
from danoan.journal_manager.control import utils

from conftest import *

from pathlib import Path
import pytest


class TestBuild:
    def create_mock_journals(self, base_path: Path):
        jm.create.create("journal-1")
        jm.create.create("journal-2")

    @pytest.mark.parametrize("build_index", [True, False])
    def test_build_all(self, f_setup_init, tmp_path, build_index):
        self.create_mock_journals(tmp_path)
        build_location = tmp_path.joinpath("build")
        build_location.mkdir()

        build_journal(
            build_location.expanduser().as_posix(),
            build_index=build_index,
            ignore_safety_questions=True,
        )

        if build_index:
            assert build_location.joinpath("site", "index.html").exists()
        else:
            assert not build_location.joinpath("site", "index.html").exists()

        assert build_location.joinpath("site", "journal-1", "index.html").exists()
        assert build_location.joinpath("site", "journal-2", "index.html").exists()

    @pytest.mark.parametrize("build_index", [True, False])
    def test_build_by_location(self, f_setup_init, tmp_path, build_index):
        self.create_mock_journals(tmp_path)
        build_location = tmp_path.joinpath("build")
        build_location.mkdir()

        journal_2_location_folder = utils.find_journal_by_name(
            config.get_journal_data_file(), "journal-2"
        ).location_folder

        build_journal(
            build_location.expanduser().as_posix(),
            journals_locations_to_build=[journal_2_location_folder],
            build_index=build_index,
            ignore_safety_questions=True,
        )

        if build_index:
            assert build_location.joinpath("site", "index.html").exists()
        else:
            assert not build_location.joinpath("site", "index.html").exists()

        assert not build_location.joinpath("site", "journal-1", "index.html").exists()
        assert build_location.joinpath("site", "journal-2", "index.html").exists()

    @pytest.mark.parametrize(
        "build_index, journal_names_to_build",
        [(True, ["journal-1"]), (True, ["journal-1", "journal-2"]), (False, ["journal-1"])],
    )
    def test_build_by_name(self, f_setup_init, tmp_path, build_index, journal_names_to_build):
        self.create_mock_journals(tmp_path)
        build_location = tmp_path.joinpath("build")
        build_location.mkdir()

        build_journal(
            build_location.expanduser().as_posix(),
            journals_names_to_build=journal_names_to_build,
            build_index=build_index,
            ignore_safety_questions=True,
        )

        if build_index:
            assert build_location.joinpath("site", "index.html").exists()
        else:
            assert not build_location.joinpath("site", "index.html").exists()

        if "journal-2" in journal_names_to_build:
            assert build_location.joinpath("site", "journal-2", "index.html").exists()
        else:
            assert not build_location.joinpath("site", "journal-2", "index.html").exists()

        assert build_location.joinpath("site", "journal-1", "index.html").exists()

    @pytest.mark.parametrize(
        "build_location, build_index, journals_names_to_build, journals_locations_to_build, include_all_folder",
        [
            ("build", True, ["journal-1", "journal-2"], None, None),
            (None, True, ["journal-1", "journal-2"], None, None),
            (None, True, None, ["journals/journal-1"], None),
            (None, True, None, None, "journals"),
            (None, False, None, None, "journals"),
        ],
    )
    def test_build_by_build_instructions(
        self,
        f_setup_init,
        tmp_path,
        build_location,
        build_index,
        journals_names_to_build,
        journals_locations_to_build,
        include_all_folder,
    ):
        self.create_mock_journals(tmp_path.joinpath("journals"))

        default_build_location = tmp_path.joinpath("build")
        default_build_location.mkdir()

        if build_location:
            build_location = tmp_path.joinpath(build_location).expanduser().as_posix()

        if journals_locations_to_build:
            journals_locations_to_build = [
                tmp_path.joinpath(x).expanduser().as_posix() for x in journals_locations_to_build
            ]

        if include_all_folder:
            include_all_folder = tmp_path.joinpath(include_all_folder).expanduser().as_posix()

        build_instructions = model.BuildInstructions(
            build_location=build_location,
            build_index=build_index,
            journals_names_to_build=journals_names_to_build,
            journals_locations_to_build=journals_locations_to_build,
            include_all_folder=include_all_folder,
        )
        build_instructions_path = tmp_path.joinpath("build-instructions.toml")
        build_instructions.write(build_instructions_path)

        build_journal(
            default_build_location.expanduser().as_posix(),
            build_instructions_path=build_instructions_path,
            ignore_safety_questions=True,
        )

        if build_index:
            assert default_build_location.joinpath("site", "index.html").exists()
        else:
            assert not default_build_location.joinpath("site", "index.html").exists()

        assert default_build_location.joinpath("site", "journal-1", "index.html").exists()

        if journals_names_to_build or include_all_folder:
            assert default_build_location.joinpath("site", "journal-2", "index.html").exists()
        else:
            assert not default_build_location.joinpath("site", "journal-2", "index.html").exists()
