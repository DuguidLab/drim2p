# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import logging
import pathlib

import click
import h5py

from drim2p import io
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
)
@click.option(
    "-o",
    "--out",
    required=False,
    type=click.Path(
        exists=True,
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
    "--no-compression",
    required=False,
    is_flag=True,
    help="Whether to disable compression for the output HDF5 files.",
)
@click.option(
    "--aggression",
    required=False,
    type=click.IntRange(0, 9),
    help=(
        "Aggression level to use for GZIP compression. Lower means faster/worse "
        "compression, higher means slower/better compression."
    ),
)
@click.option(
    "--force",
    required=False,
    is_flag=True,
    help="Whether to overwrite output files if they exist.",
)
def convert_raw(
    source: pathlib.Path | None = None,
    out: pathlib.Path | None = None,
    recursive: bool = False,
    no_compression: bool = False,
    aggression: int = 4,
    force: bool = False,
) -> None:
    """Converts RAW data and metadata to HDF5.

    Note that SOURCE can be either a single file or a directory. If it is a directory,
    all the RAW files it contains will be converted.

    The metadata is expected to exist alongside the RAW file(s). The INI file should
    have the same name with only the extension changed to `.ini`. The OME-XML file is
    optional if the INI metadata contains a string of it. Otherwise, the OME-XML file
    should have the same name except for `_XYT` replaced with `_OME` and the extension
    changed to `.xml`.
    \f

    Args:
        source (pathlib.Path | None, optional):
            Source file or directory to convert. If a directory, the default is to look
            for RAW files inside of it without recursion.
        out (pathlib.Path | None, optional):
            Optional output directory for converted files.
        recursive (bool, optional):
            Whether to search directories recursively when looking for RAW files.
        no_compression (bool, optional):
            Whether to disable compression for the output HDF5 files.
        aggression (int, optional):
            Aggression level to use for GZIP compression. Lower means faster/worse
            compression, higher means slower/better compression. This should be in the
            range 0 <= value <= 9.
        force (bool, optional): Whether to overwrite output files if they exist.
    """
    # Follow `click` recommended best-practice and NO-OP if no source is given.
    # See https://github.com/pallets/click/blob/2d610e36a429bfebf0adb0ca90cdc0585f296369/docs/arguments.rst?plain=1#L43
    if source is None:
        return

    # Collect RAW file paths to convert
    _logger.debug("Collecting RAW paths.")
    raw_paths = [source]
    if source.is_dir():
        raw_paths = io.collect_paths_from_extensions(
            source, [".raw"], recursive, strict=True
        )
    _logger.debug(f"{len(raw_paths)} path(s) collected.")

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
        ini_metadata_path = path.with_suffix(".ini")
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
            xml_metadata_path = path.with_stem(
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

        shape, dtype = raw_io.parse_essential_metadata_from_ome_xml(xml_string)

        # Convert RAW to numpy
        _logger.debug(f"Reading as array using metadata: {shape=}, {dtype=}.")
        array = raw_io.read_raw_as_numpy(path, shape, dtype)

        # Output as HDF5
        _logger.debug(f"Writing to HDF5 ({out_path}).")
        compression = None if no_compression else "gzip"
        compression_opts = None if no_compression else aggression
        with h5py.File(out_path, "w") as handle:
            dataset = handle.create_dataset(
                "data",
                data=array,
                compression=compression,
                compression_opts=compression_opts,
            )

            for key, value in ini_metadata.items():
                dataset.attrs[key] = value
