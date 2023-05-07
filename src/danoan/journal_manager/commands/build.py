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
from typing import List, Iterator, Iterable, Any, Optional, Dict, Tuple


class NamesNotFoundInRegistry(Exception):
    def __init__(self, names: Iterable[str]):
        self.names = names


class InvalidLocations(Exception):
    def __init__(self, locations: Iterable[str]):
        self.locations = locations


class IncludeAllFolderDoesNotExist(Exception):
    def __init__(self, path: str):
        self.path = path


def register_journals_by_location(locations: List[str]):
    """
    Register journals by location in the registry.

    If a location is invalid, no journal is registered and, instead,
    a InvalidLocations exception is raised.
    """
    invalid_locations: List[str] = []
    for journal_location in locations:
        if not Path(journal_location).exists():
            invalid_locations.append(journal_location)

    if len(invalid_locations) != 0:
        raise InvalidLocations(invalid_locations)

    for journal_location in locations:
        print(f"Registering journal location: {journal_location}")
        register_journal(journal_location)


def collect_journal_names_from_location(list_of_locations: List[str]) -> List[str]:
    journal_data_file = config.get_journal_data_file()
    return list(
        map(lambda x: utils.find_journal_by_location(journal_data_file, x).name, list_of_locations)
    )


def validate_journal_names_in_registry(names: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separate a list of journal names in registered and non registered.
    """
    journal_data_file = config.get_journal_data_file()
    registered_names = list(
        filter(lambda x: utils.find_journal_by_name(journal_data_file, x), names)
    )
    non_registered_names = list(filter(lambda x: x not in registered_names, names))

    return registered_names, non_registered_names


def validate_journal_locations_in_registry(
    locations: List[str],
) -> Tuple[List[str], List[str]]:
    """
    Separate a list of journal locations in registered and non registered.
    """
    journal_data_file = config.get_journal_data_file()
    registered_locations = list(
        filter(lambda x: utils.find_journal_by_location(journal_data_file, x), locations)
    )
    non_registered_locations = list(filter(lambda x: x not in registered_locations, locations))

    return registered_locations, non_registered_locations


def validate_journal_from_include_all_folder(
    include_all_folder: str,
) -> Tuple[List[str], List[str]]:
    """
    Separate a list of journal locations in registered and non registered.

    All folders located in include_all_folder are considered as a journal location.
    """
    p = Path(include_all_folder)
    if not p.exists():
        raise IncludeAllFolderDoesNotExist(include_all_folder)

    return validate_journal_locations_in_registry(list(map(lambda x: x.as_posix(), p.iterdir())))


def get_journals_names_to_build(build_instructions: model.BuildInstructions):
    """
    Read the build instructions and collect the journal names to build.

    There are four ways to build journals:
        1. Giving a list of journal names;
        2. Giving a list of journal locations;
        3. Giving a directory that contains journal folders and build all of them;
        4. Saying nothing and then all registered journals are built.

    This function reads the build instructions and extracts the journals names
    accordingly with the chosen method.
    """
    journal_data_file = config.get_journal_data_file()

    journals_names_to_build = []
    try:
        if build_instructions.journals_names_to_build is not None:
            registered_names, non_registered_names = validate_journal_names_in_registry(
                build_instructions.journals_names_to_build
            )

            if len(non_registered_names) != 0:
                raise NamesNotFoundInRegistry(non_registered_names)

            journals_names_to_build = registered_names
        elif build_instructions.journals_locations_to_build is not None:
            registered_locations, non_registered_locations = validate_journal_locations_in_registry(
                build_instructions.journals_locations_to_build
            )
            register_journals_by_location(non_registered_locations)

            journals_names_to_build = collect_journal_names_from_location(
                registered_locations + non_registered_locations
            )

        elif build_instructions.include_all_folder is not None:
            (
                registered_locations,
                non_registered_locations,
            ) = validate_journal_from_include_all_folder(build_instructions.include_all_folder)
            register_journals_by_location(non_registered_locations)

            journals_names_to_build = collect_journal_names_from_location(
                registered_locations + non_registered_locations
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
    except InvalidLocations as ex:
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
    """
    Base class for a build step in the process of building a journal.

    This class defined the interface and also the basic implementations
    of the methods that made the BuildStep interface.

    The design of the journal build process expects build steps to be
    called in a chain. For example:

        MyFirstBuildStep(some_parameters)
        .build()
        .next(MySecondBuildStep(another_parameters))

    The parameters passed to a build step persist for the following step.
    If a parameter of same name had been set before, it will be overwritten.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def build(self, **kwargs):
        return self

    def next(self, build_step_class):
        return build_step_class(**self.__dict__).build()

    def __getitem__(self, key):
        return self.__dict__[key]


class FailedStep(BuildStep):
    """
    BuildStep to be returned whenever an error is detected.
    """

    def __init__(self, build_step: BuildStep, msg: str):
        self.build_step = build_step
        self.msg = msg

    def build(self):
        return self

    def next(self, build_step):
        return self


class BuildJournals(BuildStep):
    """
    Build html static pages from journals using mkdocs
    """

    def __init__(self, build_instructions: model.BuildInstructions, **kwargs):
        super().__init__(**kwargs)
        self.build_instructions = build_instructions
        self.journals_site_folder = Path(self.build_instructions.build_location).joinpath("site")

    def build(self):
        try:
            data: Dict[str, Any] = {"journals": []}
            for journal_name in get_journals_names_to_build(self.build_instructions):
                journal_data_file = config.get_journal_data_file()
                journal_data = utils.find_journal_by_name(journal_data_file, journal_name)
                print(journal_name)
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
    """
    Build the index page with links to all rendered journals.
    """

    assets = files("danoan.journal_manager.templates").joinpath("material-index", "assets")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Not really necessay, but this make explicit the variables that are inherit
        # by other build steps and that are necessary to be defined at this point. It
        # is also useful as a sanity check during static type checking
        self.journals_site_folder = self.__dict__["journals_site_folder"]
        self.build_instructions: model.BuildInstructions = self.__dict__["build_instructions"]

    def build(self):
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
    """
    Sets up the http server that will serve the journals.

    The http server structure is composed of:
        1. An http server written in node.js + express
        2. A file monitor script using entr
        3. A file monitor action to rebuild journals that are updated

    The http server and the file monitor run independently. Whenever a
    markdown file is modified, the file monitor triggers the file monitor
    action scripts that rebuilds only the journal affected. The http server
    will automatically reflect the changes.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.http_server_folder = Path(self.build_instructions.build_location).joinpath(
            "http-server"
        )

        # Not really necessay, but this make explicit the variables that are inherit
        # by other build steps and that are necessary to be defined at this point. It
        # is also useful as a sanity check during static type checking
        self.journals_site_folder = self.__dict__["journals_site_folder"]
        self.build_instructions: model.BuildInstructions = self.__dict__["build_instructions"]

    def build(self):
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
    """
    Start a local http server.

    This function is offered as as a helper for test purposes. It expects
    that the structure of the http_server_folder is exactly the same created
    by the BuildHttpServer build step.
    """
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


def merge_build_instructions(
    build_location: Path, build_instructions_path: Optional[Path], **kwargs
):
    """
    Helper function to merge build instructions.

    The cli parser offer several options to build journals. This helper function
    merge all these parameters in a unique object.
    """
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
    build_location: Path,
    build_instructions_path: Optional[Path] = None,
    build_index: Optional[bool] = None,
    journals_names_to_build: Optional[List[str]] = None,
    journals_locations_to_build: Optional[List[str]] = None,
    with_http_server: Optional[bool] = None,
    ignore_safety_questions: bool = False,
    **kwargs,
):
    """
    Build html static pages from journals.
    """
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

    build_instructions = merge_build_instructions(
        build_location.expanduser(),
        build_instructions_path,
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
    command_description = "Render journals in a static web page"

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
        type=Path,
        default=Path.cwd(),
    )
    parser.add_argument(
        "--build-instructions",
        dest="build_instructions_path",
        type=Path,
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
