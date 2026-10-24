"""Graph state: one job per CV, passed between nodes."""
import operator
from typing import Annotated, Any, TypedDict


class JobState(TypedDict, total=False):
    message_id: str
    filename: str
    text: str
    drive_id: str
    raw: dict[str, str]
    record: dict[str, Any]
    match: dict[str, Any]
    issues: list[str]
    review: dict[str, Any]
    attempts: int
    error: str
    status: str
    trace: Annotated[list[str], operator.add]
