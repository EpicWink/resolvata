"""Related data asset path resolving."""

import io
import abc
import typing as t

T = t.TypeVar("T")


class _FileProxy:  # TODO: unit-test
    def __init__(
        self, proxied: io.IOBase, close_callback: t.Callable[[], None] = None
    ) -> None:
        self.proxied = proxied
        self.close_callback = close_callback

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.proxied)

    def __getattribute__(self, item):
        if item == "close":
            return super().__getattribute__(item)
        return getattr(self.proxied, item)

    def close(self) -> None:
        if self.close_callback:
            self.close_callback()
        self.proxied.close()


class PathResolverABC(metaclass=abc.ABCMeta):  # TODO: unit-test
    """Base path-resolver base class."""

    _proxy_cls = _FileProxy

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

    def open(self, name: str, mode: str = "r") -> _FileProxy:
        """Open file for reading or writing as a stream.

        Args:
            name: name of file to open
            mode: mode to open as (support 'rwbt', see ``open`` for help)

        Returns:
            proxy file-object, which will write on close

        Raises:
            ValueError: on invalid mode
        """

        if sum(c in mode for c in "rw") != 1:
            raise ValueError("Need one of 'rw' in mode: %s" % mode)
        if sum(c in mode for c in "bt") == 2:
            raise ValueError("Need at most one of 'bt' in mode: %s" % mode)
        if any(c not in "rwbt" for c in mode):
            raise ValueError("Invalid characters in mode (valid are 'rwbt'): %s" % mode)

        close_callback = None
        if "w" in mode:

            def close_callback():
                stream.seek(0)
                self.write_from(name, stream)

        stream = io.BytesIO()
        if "r" in mode:
            self.read_into(name, stream)
            stream.seek(0)
        stream_text = stream
        if "b" not in mode:
            stream_text = io.TextIOWrapper(stream, write_through=True)
        return self._proxy_cls(stream_text, close_callback)


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
