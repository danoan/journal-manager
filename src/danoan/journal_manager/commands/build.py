from danoan.journal_manager.control import config, model, utils
from danoan.journal_manager.control.wrappers import general_proc_call, mkdocs_wrapper, node_wrapper

from danoan.journal_manager.commands.journal_commands.register import register as register_journal

import multiprocessing
import argparse
from importlib_resources import files, as_file
from jinja2 import Environment, PackageLoader
from pathlib import Path
import shutil
import signal
from typing import List, Iterable, Any, Optional, Dict


class NamesNotFoundInRegistry(Exception):
    def __init__(self, names: List[str]):
        self.names = names


class LocationsNotFoundInRegistry(Exception):
    def __init__(self, locations: List[str]):
        self.locations = locations


class IncludeAllFolderDoesNotExist(Exception):
    def __init__(self, path: str):
        self.path = path


def collect_from_names(names: Iterable[str]):
    journal_data_file = config.get_journal_data_file()
    unmatched_names = filter(lambda x: not utils.find_journal_by_name(journal_data_file, x), names)

    is_empty, unmatched_names = utils.peek_is_empty(unmatched_names)
    if not is_empty:
        raise NamesNotFoundInRegistry(unmatched_names)

    return names


def collect_from_locations(locations: Iterable[str]):
    # This is necessary otherwise the iterator is exhausted after the first
    # use and it returns nothing afterwards
    list_of_locations = list(locations)

    journal_data_file = config.get_journal_data_file()
    unmatched_locations = filter(
        lambda x: not utils.find_journal_by_location(journal_data_file, x),
        list_of_locations,
    )

    is_empty, unmatched_locations = utils.peek_is_empty(unmatched_locations)
    for journal_location in unmatched_locations:
        print(f"Registering journal location: {journal_location}")
        register_journal(journal_location)

    # Getting again bacause some journals may have been registered since last time
    journal_data_file = config.get_journal_data_file()

    return map(
        lambda x: utils.find_journal_by_location(journal_data_file, x).name,
        list_of_locations,
    )


def collect_from_include_all_folder(include_all_folder: str):
    p = Path(include_all_folder)
    if not p.exists:
        raise IncludeAllFolderDoesNotExist(include_all_folder)

    return collect_from_locations(map(lambda x: x.as_posix(), p.iterdir()))


def get_journals_names_to_build(build_instructions: model.BuildInstructions):
    journal_data_file = config.get_journal_data_file()

    journals_names_to_build = []
    try:
        if build_instructions.journals_names_to_build is not None:
            journals_names_to_build = collect_from_names(build_instructions.journals_names_to_build)
        elif build_instructions.journals_locations_to_build is not None:
            journals_names_to_build = collect_from_locations(
                build_instructions.journals_locations_to_build
            )
        elif build_instructions.include_all_folder is not None:
            journals_names_to_build = collect_from_include_all_folder(
                build_instructions.include_all_folder
            )
        else:
            # Build all registered journals
            journals_names_to_build.extend(
                map(lambda x: x.name, journal_data_file.list_of_journal_data)
            )
    except NamesNotFoundInRegistry as ex:
        print("The following journal names are not part of the registry:")
        for journal_name in ex.names:
            print(f"{journal_name}")
        print("Build is aborted.")
        exit(1)
    except LocationsNotFoundInRegistry as ex:
        print("The following journal location folders were not found in the registry:")
        for journal_location in ex.locations:
            print(f"{journal_location}")
        print("Build is aborted.")
        exit(1)
    except IncludeAllFolderDoesNotExist as ex:
        print(
            f"The path specified in the build instructions: {ex.path} does not exist. Build is aborted."
        )
        exit(1)

    return journals_names_to_build


class BuildStep:
    def __init__(self, build_instructions: model.BuildInstructions = None, **kwargs):
        self.build_instructions = build_instructions
        self.journals_site_folder = Path(self.build_instructions.build_location).joinpath("site")
        self.__dict__.update(**kwargs)

    def build(self, **kwargs):
        if self.build_instructions is None:
            return FailedStep(self, "build_instructions are not available")

        return self

    def next(self, build_step_class):
        return build_step_class(**self.__dict__).build()

    def __getitem__(self, key):
        return self.__dict__[key]


class FailedStep(BuildStep):
    def __init__(self, build_step: BuildStep, msg: str):
        self.build_step = build_step
        self.msg = msg

    def build(self):
        return self

    def next(self, build_step):
        return self


class BuildJournals(BuildStep):
    def build(self):
        build_result = super().build()
        if isinstance(build_result, FailedStep):
            return build_result

        try:
            data = {"journals": []}
            for journal_name in get_journals_names_to_build(self.build_instructions):
                journal_data_file = config.get_journal_data_file()
                journal_data = utils.find_journal_by_name(journal_data_file, journal_name)
                if journal_data.name == journal_name and journal_data.active:
                    mkdocs_wrapper.build(
                        Path(journal_data.location_folder),
                        f"{self.journals_site_folder}/{journal_data.name}",
                    )
                    data["journals"].append(journal_data)

            self.journal_data = data
            return self
        except BaseException as ex:
            return FailedStep(self, str(ex))


class BuildIndexPage(BuildStep):
    assets = files("danoan.journal_manager.templates").joinpath("material-index", "assets")

    def build(self):
        build_result = super().build()
        if isinstance(build_result, FailedStep):
            return build_result

        try:
            if not self.build_instructions.build_index:
                return self

            env = Environment(
                loader=PackageLoader("danoan.journal_manager", package_path="templates")
            )

            with as_file(BuildIndexPage.assets) as assets_path:
                shutil.copytree(assets_path, self.journals_site_folder.joinpath("assets"))

            with open(self.journals_site_folder.joinpath("index.html"), "w") as f:
                template = env.get_template("material-index/index.tpl.html")
                f.write(template.render(self["journal_data"]))

            return self
        except BaseException as ex:
            return FailedStep(self, str(ex))


class BuildHttpServer(BuildStep):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.http_server_folder = Path(self.build_instructions.build_location).joinpath(
            "http-server"
        )

    def build(self):
        build_result = super().build()
        if isinstance(build_result, FailedStep):
            return build_result

        try:
            if not self.build_instructions.with_http_server:
                return self

            env = Environment(
                loader=PackageLoader("danoan.journal_manager", package_path="templates")
            )

            http_server = files("danoan.journal_manager.templates").joinpath("http-server")
            shutil.copytree(http_server, self.http_server_folder)

            node_wrapper.install_dependencies(self.http_server_folder)

            file_monitor_action_template = env.get_template(
                "file-monitor/file-monitor-action.tpl.sh"
            )
            file_monitor_template = env.get_template("file-monitor/file-monitor.tpl.sh")

            file_monitor_folder = Path(self.build_instructions.build_location).joinpath(
                "file-monitor"
            )
            file_monitor_folder.mkdir(exist_ok=True)

            self.file_monitor_script = file_monitor_folder.joinpath("file-monitor.sh")
            file_monitor_action_script = file_monitor_folder.joinpath("file-monitor-action.sh")

            data = {
                "journals_site_folder": self.journals_site_folder,
                "journals_files_folder": config.get_configuration_file().default_journal_folder,
            }

            with open(self.file_monitor_script, "w") as f:
                f.write(file_monitor_template.render(data=data))
            self.file_monitor_script.chmod(0o777)

            with open(file_monitor_action_script, "w") as f:
                f.write(file_monitor_action_template.render(data=data))
            file_monitor_action_script.chmod(0o777)

            return self
        except BaseException as ex:
            return FailedStep(self, str(ex))


def start_http_server(http_server_folder: Path, file_monitor_script: Path):
    t1 = multiprocessing.Process(
        target=node_wrapper.start_server, args=[http_server_folder.joinpath("init.js")]
    )
    t2 = multiprocessing.Process(target=general_proc_call.start, args=[file_monitor_script])

    t1.start()
    t2.start()

    def terminate_processes(sig, frame):
        print("Terminating http server")
        t1.terminate()
        print("Terminating file-monitor")
        t2.terminate()

    signal.signal(signal.SIGINT, terminate_processes)
    signal.signal(signal.SIGTERM, terminate_processes)

    while t1.is_alive() and t2.is_alive():
        t1.join(0.1)
        t2.join(0.1)


def unify_build_instructions(build_instructions_path: str, build_location: str, **kwargs):
    build_instructions = None
    if build_instructions_path is None:
        build_instructions = model.BuildInstructions(build_location)
    else:
        build_instructions = model.BuildInstructions.read(build_instructions_path)

    if not build_instructions.build_location:
        build_instructions.build_location = build_location

    for keyword, value in kwargs.items():
        if value is not None:
            build_instructions.__dict__[keyword] = value

    return build_instructions


def build(
    build_location: str,
    build_instructions_path: str = None,
    build_index: Optional[bool] = None,
    journals_names_to_build: Optional[List[str]] = None,
    journals_locations_to_build: Optional[List[str]] = None,
    with_http_server: Optional[bool] = None,
    ignore_safety_questions: bool = False,
    **kwargs,
):
    build_location = Path(build_location).absolute()

    if build_location.exists():
        if not ignore_safety_questions:
            ok_continue = input(
                f"The directory {build_location} exists already. If you continue the operation the files there will be overwritten. Are you sure you want to continue"
            )

            if ok_continue.lower() not in ["y", "yes"]:
                exit(1)

        shutil.rmtree(build_location)

    build_location.mkdir()

    build_instructions = unify_build_instructions(
        build_instructions_path,
        build_location.expanduser().as_posix(),
        build_index=build_index,
        journals_names_to_build=journals_names_to_build,
        journals_locations_to_build=journals_locations_to_build,
        with_http_server=with_http_server,
    )

    build_result = (
        BuildJournals(build_instructions=build_instructions)
        .build()
        .next(BuildIndexPage)
        .next(BuildHttpServer)
    )

    if not isinstance(build_result, FailedStep):
        if with_http_server:
            start_http_server(build_result.http_server_folder, build_result.file_monitor_script)
    else:
        print(f"Build was not successful with error: {build_result.msg}")


def get_parser(subparser_action=None):
    command_name = "build"
    command_description = "Transform journals in a static web page"

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name, description=command_description, help=command_description, aliases=["b"]
        )
    else:
        parser = argparse.ArgumentParser(command_name, description=command_description)

    parser.add_argument(
        "--build-location",
        help="Directory where build artifacts will be stored. If not specified, current working directory is used",
        default=Path.cwd(),
    )
    parser.add_argument(
        "--build-instructions",
        dest="build_instructions_path",
        help="Configuration file with build instructions.",
    )
    parser.add_argument(
        "--do-not-build-index",
        dest="build_index",
        help="The index page with the table of content won't be rebuilt",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "--journal-name",
        "--jn",
        dest="journals_names_to_build",
        action="append",
        help="Name of the journal to build",
    )
    parser.add_argument(
        "--journal-location",
        "--jl",
        dest="journals_locations_to_build",
        action="append",
        help="Location of the journal to build",
    )
    parser.add_argument(
        "--with-http-server",
        action="store_true",
        help="A http-server will be started and the journals files monitored.",
    )
    parser.add_argument(
        "--ignore-safety-questions",
        action="store_true",
        help="If specified, the program will overwrite the contents of BUILD_LOCATION without previous warning.",
    )
    parser.set_defaults(func=build)

    return parser
