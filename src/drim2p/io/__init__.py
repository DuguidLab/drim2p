# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import Iterable
import pathlib
import re


def collect_paths_from_extensions(
    root: pathlib.Path,
    extensions: Iterable[str],
    recursive: bool = False,
    strict: bool = False,
) -> list[pathlib.Path]:
    """Collects paths from a root path based on extensions.

    Args:
        root (pathlib.Path):
            Root path to start the search from. If this is a file, it is the only path
            for which the extension is matched.
        extensions (Iterable[str]):
            Extensions to check against. By default, any file that contains one of these
            in its suffixes will be matched. See `strict` for a different behaviour.
        recursive (bool, optional):
            Whether to recursively visit directories when searching.
        strict (bool, optional):
            Whether to force checked files to only have a single suffix. Bu default, the
            checked extensions can appear anywhere in the suffix list of files.

    Returns:
        A list of the matched pats.
    """

    def have_at_least_one_common_element(
        iterable1: Iterable[str], iterable2: Iterable[str]
    ) -> bool:
        return any(map(lambda x: x in iterable2, iterable1))

    collected = []

    if root.is_file():
        if have_at_least_one_common_element(
            extensions, [root.suffix] if strict else root.suffixes
        ):
            collected = [root]
        return collected

    for path in root.iterdir():
        if path.is_dir():
            if not recursive:
                continue

            collected.extend(
                collect_paths_from_extensions(path, extensions, recursive, strict)
            )
        else:
            if have_at_least_one_common_element(
                extensions, [path.suffix] if strict else path.suffixes
            ):
                collected.append(path)

    return collected


def filter_paths(
    paths: Iterable[pathlib.Path],
    include: str | None = None,
    exclude: str | None = None,
    separator: str = ";",
    strict: bool = False,
) -> list[pathlib.Path]:
    """Filters paths based on include and exclude strings.

    Args:
        paths (Iterable[pathlib.Path]): Paths to filter.
        include (str | None, optional):
            String of the include filters separated by `separator`.
        exclude (str | None, optional):
            String of the exclude filters separated by `separator`.
        separator (str, optional):
            A single-character separator used to separate different filters.
        strict (bool, optional):
            Whether to automatically exclude files that do not match any of the include
            filters event if they are not matched by any of the exclude filters.

    Returns:
        A list of the paths as filtered by the input strings.
    """
    # NO-OP if neither include nor exclude is set
    if include is None and exclude is None:
        return list(paths)

    include = split_string(include, separator) if include is not None else []
    exclude = split_string(exclude, separator) if exclude is not None else []

    # First, filter which paths should be included based on `include` and `strict`
    included = []
    for path in paths:
        for filter in include:
            if re.findall(filter, str(path)):
                included.append(path)
                continue
        if not strict or not include:
            included.append(path)

    # Then, exclude any path previously selected if it matches an `exclude`
    filtered = []
    for path in included:
        for filter in exclude:
            if re.findall(filter, str(path)):
                break
        else:
            filtered.append(path)

    return filtered


def split_string(string: str, separator: str = ";") -> list[str]:
    """Splits a string on non-escaped `separator` occurrences.

    Args:
        string (str): String to split.
        separator (str, optional): A single-character separator to split on.

    Returns:
        A list containing the substrings after splitting.
    """
    if len(separator) > 1:
        raise ValueError(f"Separator should be a single character. Got '{separator}'.")

    return re.split(
        rf"(?<!(?<!\\)\\){separator}", string
    )  # Only split on separators that are not escaped, while allowing "\\{separator}"
