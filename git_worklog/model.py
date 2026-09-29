"""Commit record used by filters and reports."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Commit:
    sha: str
    authored_at: datetime
    author: str
    subject: str
