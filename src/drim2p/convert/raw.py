# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import os
import pathlib
from typing import Any

import click
import h5py
import numpy as np

from drim2p import cli_utils, io, models
from drim2p.io import raw as raw_io

_logger = logging.getLogger(__name__)


@click.command
@click.argument(
    "source",
    required=False,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        path_type=pathlib.Path,
    ),
    callback=cli_utils.noop_if_missing,
)
@click.option(
    "--ini-path",
    required=False,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=pathlib.Path,
    ),
    help=(
        "Path to the INI file containing metadata about SOURCE. "
        "This is ignored if SOURCE is a directory."
    ),
)
@click.option(
    "--xml-path",
    required=False,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=pathlib.Path,
    ),
    help=(
        "Path to the OME-XML file containing metadata about SOURCE. "
        "This is ignored if SOURCE is a directory."
    ),
)
@click.option(
    "-o",
    "--out",
    required=False,
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=pathlib.Path,
    ),
    help=(
        "Output directory in which to put the converted files. "
        "Default is to output in the same directory as SOURCE."
    ),
)
@click.option(
    "-r",
    "--recursive",
    required=False,
    is_flag=True,
    help="Whether to search directories recursively when looking for RAW files.",
)
@click.option(
    "-i",
    "--include",
    required=False,
    default=None,
    help=(
        "Include filters to apply when searching for RAW files. "
        "This supports regular-expressions. Include filters are applied before any "
        "exclude filters."
    ),
)
@click.option(
    "-e",
    "--exclude",
    required=False,
    default=None,
    help=(
        "Exclude filters to apply when searching for RAW files. "
        "This supports regular-expressions. Exclude filters are applied after all "
        "include filters."
    ),
)
@click.option(
    "--no-compression",
    required=False,
    is_flag=True,
    help="Whether to disable compression for the output HDF5 files.",
)
@click.option(
    "--generate-timestamps",
    required=False,
    is_flag=True,
    help="Whether to generate timestamps from the notes entries of the RAW files.",
)
@click.option(
    "--force",
    required=False,
    is_flag=True,
    help="Whether to overwrite output files if they exist.",
)
def convert_raw_command(**kwargs: Any) -> None:
    """Converts RAW data and metadata to HDF5.

    Note that SOURCE can be either a single file or a directory. If it is a directory,
    all the RAW files it contains will be converted.

    If '--ini-path' is not provided, it will default to the same path as the source file
    with the extension changed to '.ini'.
    If '--xml-path' is not provided, it will default to the same path as the source file
    with the extension changed to '.xml', and the 'XYT' ending changed to 'OME'. Note
    the OME-XML path is optional if the INI file contains the OME-XML as an entry.

    If `generate_timestamps` is set, a `.notes.txt` file with the same name as the RAW
    file should also be present.
    """
    convert_raw(**kwargs)


def convert_raw(
    source: pathlib.Path,
    ini_path: pathlib.Path | None = None,
    xml_path: pathlib.Path | None = None,
    out: pathlib.Path | None = None,
    recursive: bool = False,
    include: str | None = None,
    exclude: str | None = None,
    no_compression: bool = False,
    generate_timestamps: bool = False,
    force: bool = False,
) -> None:
    """Converts RAW data and metadata to HDF5.

    Note that SOURCE can be either a single file or a directory. If it is a directory,
    all the RAW files it contains will be converted.

    If '--ini-path' is not provided, it will default to the same path as the source file
    with the extension changed to '.ini'.
    If '--xml-path' is not provided, it will default to the same path as the source file
    with the extension changed to '.xml', and the 'XYT' ending changed to 'OME'. Note
    the OME-XML path is optional if the INI file contains the OME-XML as an entry.

    If `generate_timestamps` is set, a `.notes.txt` file with the same name as the RAW
    file should also be present.

    Args:
        source (pathlib.Path):
            Source file or directory to convert. If a directory, the default is to look
            for RAW files inside of it without recursion.
        ini_path (pathlib.Path | None, optional):
            Path to the INI file containing metadata about SOURCE. This is ignored if
            SOURCE is a directory.
        xml_path (pathlib.Path | None, optional):
            Path to the XML file containing metadata about SOURCE. This is ignored if
            SOURCE is a directory.
        out (pathlib.Path | None, optional):
            Optional output directory for converted files.
        recursive (bool, optional):
            Whether to search directories recursively when looking for RAW files.
        include (str | None, optional):
            Include filters to apply when searching for RAW files. This supports
            regular-expressions. Include filters are applied before any exclude filters.
        exclude (str | None, optional):
            Exclude filters to apply when searching for RAW files. This supports
            regular-expressions. Exclude filters are applied after all include filters.
        no_compression (bool, optional):
            Whether to disable compression for the output HDF5 files.
        generate_timestamps (bool, optional):
            Whether to generate timestamps from the notes entries of the RAW files. A
            ".notes.txt" file should be present along the RAW file when this is set.
        force (bool, optional): Whether to overwrite output files if they exist.
    """
    # Collect RAW file paths to convert
    raw_paths = io.find_paths(source, [".raw"], include, exclude, recursive, True)

    # If we are going to process at least a file, ensure the output directory exists
    if len(raw_paths) > 0 and out is not None:
        # First, ensure the parent of out exists. We should only support creating a
        # single directory, not a nested hierarchy as a single typo in a path can result
        # in a lot of folders being created in a way a user might not expect.
        if not out.parent.exists():
            _logger.error(
                f"Neither provided output directory '{out}' nor its parent exist. "
                f"Aborting."
            )
            return
        os.makedirs(out, exist_ok=True)

    for path in raw_paths:
        # Shortcircuit early if we won't write
        out_path = (
            out / path.with_suffix(".h5").name
            if out is not None
            else path.with_suffix(".h5")
        )
        if out_path.exists() and not force:
            _logger.info(
                f"Skipping '{path}' as it already exists and --force is not set."
            )
            continue

        _logger.debug(f"Converting '{path}'.")

        # Retrieve INI metadata
        ini_metadata_path = ini_path or path.with_suffix(".ini")
        if not ini_metadata_path.exists():
            _logger.error(
                f"Failed to retrieve INI metadata for '{path}', skipping file. "
                f"Make sure it has the same file name as the RAW file "
                f"and it only has the '.ini' extension.",
            )
            continue
        try:
            ini_metadata = raw_io.parse_metadata_from_ini(ini_metadata_path, typed=True)
        except ValueError as e:
            _logger.warning(
                f"Failed to parse INI metadata for '{ini_metadata_path}': \n{e}."
            )
            continue

        # Retrieve XML metadata
        xml_string = ini_metadata.get("ome.xml.string")
        if xml_string is None:
            _logger.debug(
                "Failed to retrieve XML metadata from INI file. Trying to use the XML "
                "file directly."
            )
            xml_metadata_path = xml_path or path.with_stem(
                path.stem.replace("XYT", "OME")
            ).with_suffix(".xml")
            if not xml_metadata_path.exists():
                _logger.error(
                    f"Failed to retrieve OME-XML metadata from INI file or directly "
                    f"through XML file for '{path}', skipping file. "
                    f"To use the XML file, make sure it has the same file name as the "
                    f"RAW file with XYT replaced with OME, and it only has the '.xml' "
                    f"extension."
                )
                continue
            else:
                _logger.debug("Using XML string from XML file.")
                xml_string = xml_metadata_path.open().read()
        else:
            _logger.debug("Using XML string from INI file.")

        shape, dtype = raw_io.parse_metadata_from_ome(xml_string)

        # Generate timestamps if requested
        timestamps = None
        if generate_timestamps:
            timestamps = _generate_timestamps(path, ini_metadata)

        # Convert RAW to numpy
        _logger.debug(f"Reading as array using metadata: {shape=}, {dtype=}.")
        array = raw_io.read_raw_as_numpy(path, shape, dtype)

        # Output as HDF5
        _logger.debug(f"Writing to HDF5 ({out_path}).")
        compression = None if no_compression else "lzf"
        with h5py.File(out_path, "w") as handle:
            dataset = handle.create_dataset(
                "data",
                data=array,
                # Chunk per frame, same for writing but speeds up reading a lot
                chunks=(1, *shape[1:]),
                compression=compression,
                shuffle=True,
            )

            for key, value in ini_metadata.items():
                dataset.attrs[key] = value

            if timestamps is not None:
                handle.create_dataset(
                    "timestamps",
                    data=timestamps,
                    compression=compression,
                    shuffle=True,
                )


def _generate_timestamps(
    raw_path: pathlib.Path, ini_metadata: dict[str, Any]
) -> np.ndarray[Any, np.dtype[np.number]] | None:
    notes_path = raw_path.with_suffix(".notes.txt")
    if not notes_path.exists():
        _logger.error(
            "Requested to generate timestamps but notes file is not present. "
            "Skipping timestamp generation."
        )
        return None

    entries = raw_io.parse_notes_entries(notes_path.open().read())
    # Notes may have entries for multiple recordings, find the relevant one
    entries = list(filter(lambda x: x.pure_file_path.match(raw_path.name), entries))
    if len(entries) > 1:
        _logger.error(
            f"Found multiple notes entries matching RAW file '{raw_path}'. "
            f"Skipping timestamp generation."
        )
        return None
    elif len(entries) < 1:
        _logger.error(
            f"Could not find a notes entry matching RAW file '{raw_path}'. "
            f"Skipping timestamp generation."
        )
        return None

    # Only a single matched entry, good to go
    frame_count = ini_metadata.get("frame.count")
    if frame_count is None:
        _logger.error(
            f"Requested to generate timestamps but frame count could "
            f"not be retrieved from INI metadata. Skipping timestamp "
            f"generation."
        )
        return None

    timestamps = generate_timestamps_for_note_entry(entries[0], int(frame_count))
    _logger.debug(f"Generated timestamps for {int(frame_count)} frames.")
    return timestamps


def generate_timestamps_for_note_entry(
    entry: models.NotesEntry, frame_count: int
) -> np.ndarray[Any, np.dtype[np.number]]:
    """Generates a timestamps series for a given notes entry and a frame count.

    Args:
        entry (models.NotesEntry): Entry for which to generate timestamps.
        frame_count (int): Integer count of the frames for the given entry.

    Returns:
        A series of timestamps for each frame.
    """
    delta = entry.timedelta_ms
    frame_spacing = delta / frame_count

    return np.array([i * frame_spacing for i in range(frame_count)])
