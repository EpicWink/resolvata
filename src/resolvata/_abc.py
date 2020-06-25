"""Related data asset path resolving abstract base class."""

import io
import abc
import contextlib
import typing as t


class PathResolverABC(metaclass=abc.ABCMeta):  # TODO: unit-test, document
    @abc.abstractmethod
    def get_path(self, name: str) -> str:
        pass

    @abc.abstractmethod
    def read_into(self, name: str, stream: io.BytesIO) -> None:
        pass

    @abc.abstractmethod
    def write_from(self, name: str, stream: io.BytesIO) -> None:
        pass

    @contextlib.contextmanager
    def open(self, name: str, mode: str = "r") -> t.Generator[io.IOBase, None, None]:
        stream = io.BytesIO()
        if "r" in mode:
            self.read_into(name, stream)
            stream.seek(0)
        stream_text = stream
        if "b" not in mode:
            stream_text = io.TextIOWrapper(stream, write_through=True)
        try:
            yield stream_text
        finally:
            if "w" in mode:
                stream.seek(0)
                self.write_from(name, stream)
