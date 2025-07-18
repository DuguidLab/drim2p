from collections.abc import Sequence
from typing import Any


class ArrayDimensionNotSupportedError(Exception):
    def __init__(self, dimension: int) -> None:
        super().__init__(f"Only 2D arrays are supported. Found: {dimension}D.")


class InvalidPercentileError(Exception):
    def __init__(self, value: Any) -> None:
        super().__init__(f"Cannot compute percentile when it is `{value}`.")


class OutOfRangePercentileError(Exception):
    def __init__(self, percentile: int) -> None:
        super().__init__(
            f"Percentile should be between 0 and 100. Found: {percentile}. "
        )


class RollingWindowTooLargeError(Exception):
    def __init__(self, window_width: int, array_length: int) -> None:
        super().__init__(
            f"Rolling window width should be at most twice the length of the first "
            f"dimension of the input minus 1. Got '{window_width}' which is larger "
            f"than {array_length * 2 - 1}."
        )


class UnknownMethodError(Exception):
    def __init__(self, method: str, known: Sequence[str]) -> None:
        super().__init__(
            f"Unknown method: '{method}'. Valid methods are: {', '.join(known)}"
        )


class UnknownPaddingModeError(Exception):
    def __init__(self, padding_mode: str, known: Sequence[str]) -> None:
        super().__init__(
            f"Unknown padding mode '{padding_mode}'. "
            f"Valid modes are: {', '.join(known)}."
        )
