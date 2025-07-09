from typing import Any, Iterator

import numpy as np
import numpy.typing as npt
import pytest


@pytest.fixture(scope="module", params=[(100,), (20, 5)])
def np_array(request: pytest.FixtureRequest) -> Iterator[npt.NDArray[Any]]:
    yield np.arange(np.prod(request.param)).reshape(request.param)
