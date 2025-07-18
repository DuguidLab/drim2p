import pathlib
from collections.abc import Sequence


class NoINISectionsFoundError(Exception):
    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(f"Failed to parse INI metadata: no sections found. ({path})")


class TooManyINISectionsFoundError(Exception):
    def __init__(self, path: pathlib.Path, sections: Sequence[str]) -> None:
        super().__init__(
            f"Failed to parse INI metadata: too many sections found. Only a single "
            f"section (other than [DEFAULT]) is supported. "
            f"Found: {' '.join(sections)}. ({path})"
        )


class SeparatorTooLongError(Exception):
    def __init__(self, separator: str) -> None:
        super().__init__(f"Separator should be a single character. Found: {separator}.")


class UnknownCompressionError(Exception):
    def __init__(self, compression: str, known: Sequence[str]) -> None:
        super().__init__(
            f"Unknown compression: '{compression}'. "
            f"Valid compression algorithms are: {', '.join(known)}"
        )
