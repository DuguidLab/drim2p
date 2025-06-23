import os
import pathlib
from typing import Iterator

import pytest

from drim2p import io


@pytest.fixture()
def file_paths() -> Iterator[list[pathlib.Path]]:
    path = pathlib.Path()
    yield [
        path / "file123.abc",
        path / "file234.xyz",
        path / "file345.abc.xyz",
        path / "file456.xyz.abc",
        path / "subfolder" / "file123.abc",
        path / "subfolder" / "file234.xyz",
        path / "subfolder" / "file345.abc.xyz",
        path / "subfolder" / "file456.xyz.abc",
    ]


@pytest.fixture()
def build_folder(
    tmp_path: pathlib.Path,
    file_paths: list[pathlib.Path],
    request: pytest.FixtureRequest,
) -> Iterator[tuple[pathlib.Path, list[pathlib.Path], bool]]:
    """Returns a prepared directory structure for collecting paths.

    Args:
        tmp_path (pathlib.Path): Built-in Pytest fixture. Provides the root.
        file_paths (list[pathlib.Path]): Fixture providing hard-coded relative paths.
        request (pytest.FixtureRequest):
            Built-in Pytest fixture. Provides boolean for recursiveness and strictness.

    Returns:
        A tuple in the form of (root, expected, recursive, strict) where 'root' is the
        path to the prepared folder, 'expected' is a list of the expected paths after
        filtering, 'recursive' is whether the search will be recursive, an 'strict' is
        whether the search will be strict. For more details on 'recursive' and 'strict',
        see the documentation for `drim2p.io.collect_paths_from_extensions`.
    """
    paths = [tmp_path / path for path in file_paths]
    for path in paths:
        os.makedirs(path.parent, exist_ok=True)
        path.touch()

    expected = [
        tmp_path / "file234.xyz",
        tmp_path / "file345.abc.xyz",
    ]
    if request.param[0]:  # Recursive
        expected.append(tmp_path / "subfolder" / "file234.xyz")
        expected.append(tmp_path / "subfolder" / "file345.abc.xyz")
        if not request.param[1]:  # Not strict
            expected.append(tmp_path / "subfolder" / "file456.xyz.abc")
    if not request.param[1]:  # Not strict
        expected.append(tmp_path / "file456.xyz.abc")

    yield tmp_path, expected, *request.param


@pytest.mark.parametrize(
    "build_folder",
    [
        # recursive, strict
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ],
    indirect=True,
)
def test_path_collection(
    build_folder: tuple[pathlib.Path, list[pathlib.Path], bool, bool],
) -> None:
    root, expected, recursive, strict = build_folder
    actual = io.collect_paths_from_extensions(
        root, [".xyz"], recursive=recursive, strict=strict
    )

    assert sorted(actual) == sorted(expected)


# TODO: Include testing for separators
@pytest.mark.parametrize(
    "include, exclude",
    [
        (None, None),
        ("1;2;3", None),
        (None, "34"),
        ("1;2;3", "34"),
    ],
)
def test_filter_paths(
    include: str | None, exclude: str | None, file_paths: list[pathlib.Path]
) -> None:
    root = pathlib.Path()
    paths = [path for path in file_paths if path.parent == root]

    if include and exclude:
        expected = [
            root / "file123.abc",
        ]
    elif include:
        expected = [
            root / "file123.abc",
            root / "file234.xyz",
            root / "file345.abc.xyz",
        ]
    elif exclude:
        expected = [
            root / "file123.abc",
            root / "file456.xyz.abc",
        ]
    else:
        expected = paths

    actual = io.filter_paths(paths, include, exclude)

    assert sorted(actual) == sorted(expected)


@pytest.mark.parametrize(
    "string, separator, expected",
    [
        ("foo;bar", ";", ["foo", "bar"]),
        (r"foo;b\;ar", ";", ["foo", r"b\;ar"]),
        (r"foo bar foo\ bar", " ", ["foo", "bar", r"foo\ bar"]),
    ],
)
def test_split_string(string: str, separator: str, expected: list[str]) -> None:
    actual = io.split_string(string, separator)

    assert sorted(actual) == sorted(expected)
