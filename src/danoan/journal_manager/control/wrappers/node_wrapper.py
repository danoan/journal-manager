import subprocess
from pathlib import Path
import os

background_tasks = set()


def install_dependencies(http_server_location: Path):
    cwd = os.getcwd()
    os.chdir(http_server_location.expanduser().as_posix())
    npm_args = ["npm", "install"]
    subprocess.run(npm_args)
    os.chdir(cwd)


def start_server(init_script: Path):
    node_args = ["node", init_script.expanduser().as_posix()]
    subprocess.run(node_args)
