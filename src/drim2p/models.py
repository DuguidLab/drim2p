# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
import enum
import pathlib
import tomllib
from typing import Any
from typing import cast

import pydantic


class Strategy(enum.Enum):
    Markov = "HiddenMarkov2D"
    Plane = "PlaneTranslation2D"
    Fourier = "DiscreteFourier2D"

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        try:
            value = value.lower()
        except AttributeError:
            return super()._missing_(value)

        for variant in cls:
            if variant.name.lower() == value:
                return variant

        return super()._missing_(value)


class MotionConfig(pydantic.BaseModel):
    strategy: Strategy = Strategy.Fourier
    displacement: tuple[int, int] = (50, 50)

    @classmethod
    def from_file(cls, path: pathlib.Path) -> MotionConfig:
        with open(path, "rb") as handle:
            contents = tomllib.load(handle)

        dictionary = contents.get("motion-correction")
        if dictionary is None:
            raise ValueError(
                f"Cannot parse file '{path}' as a valid motion config. It does not "
                f"have a 'motion-correction' section."
            )

        return cls.from_dictionary(dictionary)

    @classmethod
    def from_dictionary(cls, dictionary: dict[str, Any]) -> MotionConfig:
        strategy = dictionary.get("strategy")
        if strategy is None:
            raise ValueError(
                "Could not find a strategy from the provided config dictionary."
            )
        try:
            strategy = Strategy(strategy)
        except ValueError:
            raise ValueError(
                f"Could not parse '{strategy}' as a valid strategy. "
                f"Valid options: {', '.join(variant.name for variant in Strategy)}."
            ) from None

        displacement = dictionary.get("displacement")
        if displacement is None:
            raise ValueError(
                "Could not find a displacement from the provided config dictionary."
            )
        if not hasattr(displacement, "__len__") or len(displacement) != 2:
            raise ValueError(
                f"Could not parse '{displacement}' as two displacement values."
            )
        try:
            displacement = cast(tuple[int, int], tuple(map(int, displacement)))
        except ValueError:
            raise ValueError(
                f"Could not parse '{displacement}' as a tuple of integers values."
            ) from None

        return cls(strategy=strategy, displacement=displacement)


class NotesEntry(pydantic.BaseModel):
    start_time: datetime.datetime
    """Start time of the notes entry recording."""
    end_time: datetime.datetime
    """End time of the notes entry recording."""
    file_path: pathlib.Path
    """File path the notes entry relates to."""

    @property
    def timedelta(self) -> datetime.timedelta:
        """Time delta between the entry's end and start times."""
        return self.end_time - self.start_time

    @property
    def timedelta_ms(self) -> float:
        """Time delta in milliseconds between the entry's end and start times."""
        return self.timedelta / datetime.timedelta(milliseconds=1)

    @property
    def pure_file_path(self) -> pathlib.PureWindowsPath:
        """A Windows file path representation of file path."""
        return pathlib.PureWindowsPath(self.file_path)
