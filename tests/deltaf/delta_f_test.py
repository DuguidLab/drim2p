import itertools
from typing import Any, get_args

import numpy.typing as npt
import pytest

from drim2p import deltaf


@pytest.mark.parametrize(
    (
        "method",
        "percentile",
        "window_width",
        "padding_mode",
        "constant_value",
    ),
    list(
        itertools.product(
            get_args(deltaf._F0Method),
            [5],
            [0, 10],
            get_args(deltaf._PaddingMode),
            [0],
        )
    ),
)
def test_compute_f0_shape(
    np_array: npt.NDArray[Any],
    method: deltaf._F0Method,
    percentile: int,
    window_width: int,
    padding_mode: deltaf._PaddingMode,
    constant_value: int,
) -> None:
    expected_shape = np_array.shape if window_width != 0 else np_array.shape[1:]
    result = deltaf.compute_f0(
        np_array, method, percentile, window_width, padding_mode, constant_value
    )

    assert result.shape == expected_shape


@pytest.mark.parametrize("percentile", (-10, 110))
def test_compute_f0_1(np_array: npt.NDArray[Any], percentile: int) -> None:
    with pytest.raises(ValueError):
        deltaf.compute_f0(np_array, method="percentile", percentile=percentile)


def test_compute_f0_2(np_array: npt.NDArray[Any]) -> None:
    with pytest.raises(ValueError):
        deltaf.compute_f0(np_array, method="invalid")  # type: ignore[arg-type]
