"""Shared event schema for algorithm playback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EventKind = Literal["start", "visit", "inspect_edge", "relax", "finish"]


@dataclass(frozen=True)
class StepEvent:
    sequence: int
    algorithm: str
    kind: EventKind
    current: str | None
    neighbor: str | None
    frontier: tuple[str, ...]
    visited: tuple[str, ...]
    distances: dict[str, float]
    predecessor: dict[str, str | None]


@dataclass(frozen=True)
class AlgorithmRun:
    algorithm: str
    start: str
    order: tuple[str, ...]
    distances: dict[str, float]
    predecessor: dict[str, str | None]
    events: tuple[StepEvent, ...]
