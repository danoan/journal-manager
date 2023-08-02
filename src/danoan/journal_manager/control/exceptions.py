from pathlib import Path
from typing import Optional, Iterable


class EmptyList(Exception):
    pass


class InvalidName(Exception):
    def __init__(self, names: Iterable[str] = []):
        self.names = names


class InvalidLocation(Exception):
    def __init__(self, locations: Iterable[Path] = []):
        self.locations = locations


class InvalidIncludeAllFolder(Exception):
    def __init__(self, path: Optional[str] = None):
        self.path = path


class InvalidTemplate(Exception):
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg
