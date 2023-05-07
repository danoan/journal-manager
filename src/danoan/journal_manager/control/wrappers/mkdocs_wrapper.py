from pathlib import Path
import os
import subprocess


def create(journal_location: Path):
    """
    Create a mkdocs journal.
    """
    subprocess.run(["mkdocs", "new", journal_location])


def build(journal_location: Path, build_location: Path):
    """
    Build a static html page with mkdocs.
    """
    cwd = os.getcwd()

    os.chdir(journal_location)
    subprocess.run(["mkdocs", "build", "-d", build_location])

    os.chdir(cwd)
