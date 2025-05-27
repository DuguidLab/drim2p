#  SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
#  SPDX-License-Identifier: MIT

import sys

import click


@click.group()
def drim2p() -> None:
    """A dreamy 2-photon imaging processing pipeline."""


if __name__ == "__main__":
    drim2p(sys.argv[1:])
