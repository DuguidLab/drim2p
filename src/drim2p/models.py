# SPDX-FileCopyrightText: © 2025 Olivier Delrée <olivierdelree@protonmail.com>
#
# SPDX-License-Identifier: MIT

import datetime
import pathlib

import pydantic


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
