from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrendSignal:
    topic: str
    score: float
    reason: str


class TrendEngine:
    """Provider-agnostic trend layer.

    Real integrations will be added using public signals and official APIs.
    The MVP deliberately does not scrape private recommendation endpoints.
    """

    def rank(self, signals: list[TrendSignal]) -> list[TrendSignal]:
        return sorted(signals, key=lambda item: item.score, reverse=True)
