# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import contextlib
import logging
import pathlib
import shutil
import time
from typing import Any
from typing import get_args

import click
import h5py
import numpy as np

from drim2p import cli_utils
from drim2p import io
from drim2p import models

_logger = logging.getLogger(__name__)


@click.command("correct")
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
    "-s",
    "--settings-path",
    required=False,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
    help="Path to the settings file to use.",
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
    "-c",
    "--compression",
    required=False,
    type=click.Choice(get_args(io.COMPRESSION), case_sensitive=False),
    default=None,
    callback=lambda _, __, x: x if x is None else x.lower(),
    help="Compression algorithm to use.",
)
@click.option(
    "--aggression",
    "compression_opts",
    required=False,
    type=click.IntRange(0, 9),
    default=4,
    help=(
        "Aggression level to use for GZIP compression. Lower means faster/worse "
        "compression, higher means slower/better compression. Ignored if "
        "'--compression' is not GZIP."
    ),
)
@click.option(
    "--force",
    required=False,
    is_flag=True,
    help="Whether to overwrite output datasets if they exist.",
)
def apply_motion_correction_command(**kwargs: Any) -> None:
    """Applies motion correction on HDF5 chunks.

    The motion correction is configured through a TOML settings file (available from
    the source code in the resources directory). The file allows customising behaviour
    such as the strategy to use or the maximum displacement allowed.
    """
    apply_motion_correction(**kwargs)


def apply_motion_correction(
    source: pathlib.Path,
    settings_path: pathlib.Path | None = None,
    recursive: bool = False,
    include: str | None = None,
    exclude: str | None = None,
    compression: io.COMPRESSION | None = None,
    compression_opts: int | None = None,
    force: bool = False,
) -> None:
    """Applies motion correction on HDF5 chunks.

    The motion correction is configured through a TOML settings file (available from
    the source code in the resources directory). The file allows customising behaviour
    such as the strategy to use or the maximum displacement allowed.

    Args:
        source (pathlib.Path):
            Source file or directory to convert. If a directory, the default is to look
            for HDF5 (.h5) files inside of it without recursion.
        settings_path (pathlib.Path | None, optional):
            Path to the settings.toml file to use to configure motion correction.
        recursive (bool, optional):
            Whether to search directories recursively when looking for HDF5 files.
        include (str | None, optional):
            Include filters to apply when searching for HDF5 files. This supports
            regular-expressions. Include filters are applied before any exclude filters.
        exclude (str | None, optional):
            Exclude filters to apply when searching for HDF5 files. This supports
            regular-expressions. Exclude filters are applied after all include filters.
        compression (io.COMPRESSION | None, optional): Compression algorithm to use.
        compression_opts (int | None, optional):
            Compression options to use with the given algorithm.
        force (bool, optional): Whether to ovewrite output datasets if they exist.
    """
    if settings_path is None:
        _logger.error("Please provide a settings file.")
        return

    # Load the settings
    settings = models.MotionConfig.from_file(settings_path)

    for path in io.find_paths(source, [".h5"], include, exclude, recursive, True):
        _logger.debug(f"Motion correcting '{path}'.")

        _apply_motion_correction(path, settings, compression, compression_opts, force)


def _apply_motion_correction(
    path: pathlib.Path,
    settings: models.MotionConfig,
    compression: io.COMPRESSION | None,
    compression_opts: int | None,
    force: bool = False,
) -> None:
    # Lazy time-consuming import
    import sima

    # Keep own handle to check for motion correction dataset
    file = h5py.File(path, "a", locking=False)

    if has_a_motion_corrected_dataset(file) and not force:
        _logger.info(
            f"Skipping '{path}' as it was already corrected and --force is not set."
        )
        return

    # Retrieve strategy object
    match settings.strategy:
        case models.Strategy.Markov:
            strategy = sima.motion.HiddenMarkov2D(
                granularity="plane",
                max_displacement=settings.displacement,
                verbose=True,
            )
        case models.Strategy.Plane:
            strategy = sima.motion.PlaneTranslation2D(
                max_displacement=settings.displacement
            )
        case models.Strategy.Fourier:
            strategy = sima.motion.DiscreteFourier2D(
                max_displacement=settings.displacement
            )
        case _:
            message = f"Strategy '{settings.strategy}' not implemented"  # type: ignore[unreachable]
            raise NotImplementedError(message)

    # Start motion correction
    _logger.info(
        f"Applying motion correction for '{path.stem}' using {settings.strategy.value}."
    )
    start_time = time.perf_counter()

    # Where sima puts dataset information during motion correction.
    # SIMA uses 'os.makedirs' without 'exist_ok' so we need to make sure there isn't
    # a cache already (e.g., something prevented a previous run from completing).
    temp_sima_dataset_path = path.parent / f".{path.with_suffix('.sima').name}"
    if temp_sima_dataset_path.exists():
        _logger.debug("Deleting existing SIMA folder.")
        shutil.rmtree(temp_sima_dataset_path)

    # Create a `Sequence` object from the HDF5 file that sima understands
    sequences = [
        sima.Sequence.create("HDF5", path, key=io.ACQ_IMAGING_PATH, dim_order="tyx")
    ]
    # Motion correct
    dataset, displacements = strategy.correct(sequences, temp_sima_dataset_path)

    duration = time.perf_counter() - start_time
    hours, duration = divmod(duration, 3600)
    minutes, duration = divmod(duration, 60)
    time_string = f"{hours:.0f}h {minutes:.0f}m {duration:.2f}s"
    _logger.info(f"Finished motion correction in {time_string}.")

    # Save motion corrected dataset and displacements
    if has_a_motion_corrected_dataset(file):  # Remote corrected dataset if it exists
        _logger.debug(
            f"Removing existing motion corrected 'imaging' dataset from '{path}'."
        )
        del file[io.MOT_IMAGING_PATH]

    compression, compression_opts, shuffle = io.get_h5py_compression_parameters(
        compression, compression_opts
    )
    _logger.debug(
        f"Saving 'imaging' dataset to '{path}' "
        f"({compression=}, {compression_opts=}, {shuffle=})."
    )

    # Manually save the motion-corrected sequence instead of using dataset.export_frames
    # to avoid extra dimensions, and because we're a bit faster when working with larger
    # files, and because SIMA saves it as float64 with no decimal part (?) and we can
    # save 3/4 of the space by keeping it uint16.
    sequence = dataset.sequences[0]
    shape = sequence.shape
    imaging_dataset = file.create_dataset(
        io.MOT_IMAGING_PATH,
        shape=shape[0:1] + shape[2:4],
        dtype=np.uint16,
        chunks=(1, *shape[2:4]),
        compression=compression,
        compression_opts=compression_opts,
        shuffle=shuffle,
    )
    for i, frame in enumerate(iter(sequence)):
        # No need to use `np.round` as the decimal part is seemingly always 0
        imaging_dataset[i] = frame.squeeze().astype(np.uint16)

    _logger.debug("Saving displacements.")

    displacements = displacements[0].squeeze()  # Go from 1xTx1x2 to Tx2
    with contextlib.suppress(KeyError):  # Ensure it doesn't exist
        del file[io.MOT_DISPLACEMENTS_PATH]
    file.create_dataset(io.MOT_DISPLACEMENTS_PATH, data=displacements)

    # Save some information about the settings used
    imaging_dataset.attrs["STRATEGY"] = settings.strategy.name
    imaging_dataset.attrs["MAX_DISPLACEMENT"] = settings.displacement
    imaging_dataset.attrs["PROCESSING_TIME"] = time_string

    _logger.info("Saved motion correction to file.")

    _logger.debug("Cleaning up sima directory.")
    shutil.rmtree(
        temp_sima_dataset_path,
        onexc=lambda *_: _logger.debug("Failed to delete sima directory."),
    )


def has_a_motion_corrected_dataset(handle: h5py.File) -> bool:
    """Returns whether the given handle has an existing motion-corrected dataset.

    Args:
        handle (h5py.File): Handle to check.

    Returns:
        Whether such a dataset exists.
    """
    return handle.get(io.MOT_IMAGING_PATH) is not None
