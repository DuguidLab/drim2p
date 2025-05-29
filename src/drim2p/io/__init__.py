# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import Iterable
import pathlib


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
