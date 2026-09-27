"""Small, UI-independent cursor over an immutable algorithm event sequence."""

from __future__ import annotations

from dataclasses import dataclass

from .events import AlgorithmRun, StepEvent


@dataclass
class Playback:
    run: AlgorithmRun
    index: int = -1

    @property
    def current(self) -> StepEvent | None:
        if self.index < 0 or not self.run.events:
            return None
        return self.run.events[self.index]

    @property
    def finished(self) -> bool:
        return not self.run.events or self.index >= len(self.run.events) - 1

    def step(self) -> StepEvent | None:
        if self.finished:
            return self.current
        self.index += 1
        return self.current

    def reset(self) -> None:
        self.index = -1
