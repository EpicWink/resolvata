"""Related data asset path resolving."""

import io
import abc
import contextlib
import typing as t

T = t.TypeVar("T")


class PathResolverABC(metaclass=abc.ABCMeta):  # TODO: unit-test
    """Base path-resolver base class."""

    @abc.abstractmethod
    def get_path(self, name: str) -> str:
        """Get the full path for a file.

        Concrete subclasses should document the path's format.

        Args:
            name: name of file

        Returns:
            file path
        """

    @abc.abstractmethod
    def read_into(self, name: str, stream: io.BytesIO) -> None:
        """Read file data into a stream.

        Args:
            name: name of file to read
            stream: stream to read into
        """

    @abc.abstractmethod
    def write_from(self, name: str, stream: io.BytesIO) -> None:
        """Write file data from a stream.

        Args:
            name: name of file to write
            stream: stream to write from
        """

    @contextlib.contextmanager
    def open(self, name: str, mode: str = "r") -> t.Generator[io.IOBase, None, None]:
        """Open file for reading or writing as a stream.

        Args:
            name: name of file to open
            mode: mode to open as

        Returns:
            file proxy context-manager
        """

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


class ObjectResolverABC(PathResolverABC, t.Generic[T], metaclass=abc.ABCMeta):  # TODO: unit-test
    """Base path-resolver abstract class, with object serialisation methods."""

    @abc.abstractmethod
    def load(self, stream: io.BytesIO) -> T:
        """Deserialise object from stream.

        Args:
            stream: stream to load from

        Returns:
            loaded object
        """

    @abc.abstractmethod
    def dump(self, item: T, stream: io.BytesIO) -> None:
        """Serialise object to stream.

        Args:
            item: item to dump
            stream: stream to load from
        """

    def get(self, name: str) -> T:
        """Get an object.

        Args:
            name: object name

        Returns:
            loaded object
        """

        stream = io.BytesIO()
        self.read_into(name, stream)
        stream.seek(0)
        return self.load(stream)

    def put(self, name: str, item: T) -> None:
        """Put an object.

        Args:
            name: object name
            item: object to put
        """

        stream = io.BytesIO()
        self.dump(item, stream)
        stream.seek(0)
        self.write_from(name, stream)


class LocalResolver(PathResolverABC):  # TODO: unit-test
    """Local path resolver."""

    def __init__(self, parent: str) -> None:
        """Initialise local resolver

        Args:
            parent: parent directory
        """

        import pathlib

        self.parent = pathlib.Path(parent)

    def get_path(self, name):
        """Get the full path for a file.

        Args:
            name: name of file

        Returns:
            file path
        """

        return str(self.parent / name)

    def read_into(self, name, stream):
        with open(self.get_path(name), "rb") as f:
            stream.write(f.read())

    def write_from(self, name, stream):
        with open(self.get_path(name), "wb") as f:
            f.write(stream.read())
