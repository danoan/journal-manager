from pathlib import Path
import os
import subprocess


def create(journal_location: Path):
    cmd_args = ["mkdocs", "new", journal_location]
    subprocess.run(cmd_args)


def build(journal_location: Path, build_location: Path):
    cwd = os.getcwd()

    os.chdir(journal_location)
    cmd_args = ["mkdocs", "build", "-d", build_location]
    subprocess.run(cmd_args)

    os.chdir(cwd)
