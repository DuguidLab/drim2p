#  SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
#  SPDX-License-Identifier: MIT

import logging
import sys

import click

from drim2p import convert, draw, logging_, motion

_logger = logging.getLogger("drim2p")


@click.group(invoke_without_command=True)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    required=False,
    count=True,
    help=(
        "Set verbosity level. Level 0 is WARNING (default). Level 1 is INFO. "
        "Level 2 is DEBUG."
    ),
)
@click.option(
    "--no-colour",
    required=False,
    is_flag=True,
    help="Disable logging colours.",
)
def drim2p(verbosity: int = 0, no_colour: bool = False) -> None:
    """A dreamy 2-photon imaging processing pipeline.
    \f

    Args:
        no_colour (bool, optional): Whether to disable logging colours.
        verbosity (int, optional):
            Verbosity level. Level 0 is WARNING (default). Level 1 is INFO. Level 2 is
            DEBUG.
    """
    set_up_logging(verbosity, no_colour)


def set_up_logging(level: int, no_colour: bool) -> None:
    if no_colour:
        _formatter = logging.Formatter(
            "[{asctime}] - [{levelname:>9s} ] - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        _formatter = logging_.ColourFormatter()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(_formatter)

    _logger.addHandler(console_handler)

    if level == 1:
        _logger.setLevel(logging.INFO)
    elif level > 1:
        _logger.setLevel(logging.DEBUG)


drim2p.add_command(convert.convert)
drim2p.add_command(motion.motion)
drim2p.add_command(draw.draw)


if __name__ == "__main__":
    drim2p(sys.argv[1:])
