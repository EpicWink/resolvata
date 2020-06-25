import pathlib

from . import _abc


class LocalResolver(_abc.PathResolverABC):  # TODO: unit-test, document
    def __init__(self, parent: str) -> None:
        self.parent = pathlib.Path(parent)

    def get_path(self, name):
        return str(self.parent / name)

    def read_into(self, name, stream):
        with open(self.get_path(name), "rb") as f:
            stream.write(f.read())

    def write_from(self, name, stream):
        with open(self.get_path(name), "wb") as f:
            f.write(stream.read())
