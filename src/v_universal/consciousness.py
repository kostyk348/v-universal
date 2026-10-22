"""V-CONSCIOUSNESS — sensations as trunk, thoughts as versions.

A toy "stream of consciousness" model. Sensations and emotions are the
trunk; each thought is staged in a draft; committing the draft appends
the thought to the trunk and stores the latest decision. Aborting the
draft models regret — the thought happened, but did not become a
decision.
"""

from __future__ import annotations

from v_universal.core import VLayer, VVersion

_DEFAULT_SENSATIONS = {
    "light": 0.5,
    "sound": 0.3,
    "touch": 0.2,
    "pain": 0.0,
}

_DEFAULT_EMOTIONS = {
    "joy": 0.5,
    "fear": 0.1,
    "anger": 0.0,
}


class VConsciousness:
    """A tiny state machine modelling sensations, emotions, thoughts."""

    def __init__(
        self,
        sensations: dict[str, float] | None = None,
        emotions: dict[str, float] | None = None,
    ) -> None:
        self.mind = VLayer("MIND:Sensations")
        self.mind.set_base("sensations", dict(sensations or _DEFAULT_SENSATIONS))
        self.mind.set_base("emotions", dict(emotions or _DEFAULT_EMOTIONS))
        self.mind.set_base("thoughts", [])
        self.mind.set_base("decision", None)
        self.mind.crystallize()

    def think(self, version: VVersion, thought: str) -> None:
        """Append ``thought`` to ``version``'s thought stream."""

        thoughts = list(version.read("thoughts"))
        thoughts.append(thought)
        version.write("thoughts", thoughts)

    def decide(self, version: VVersion, decision: str) -> None:
        """Stage a decision into ``version``'s draft."""

        version.write("decision", decision)

    def feel(self, version: VVersion, emotion: str, intensity: float) -> None:
        """Update the intensity of ``emotion`` within ``version``'s draft."""

        emotions = dict(version.read("emotions"))
        emotions[emotion] = float(intensity)
        version.write("emotions", emotions)

    def thoughts(self) -> list[str]:
        return list(self.mind.get("thoughts"))

    def decision(self) -> str | None:
        return self.mind.get("decision")
