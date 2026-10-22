"""Tests for :class:`v_universal.consciousness.VConsciousness`."""

from __future__ import annotations

from v_universal.consciousness import VConsciousness


def test_default_sensations_and_emotions() -> None:
    m = VConsciousness()
    assert m.mind.get("sensations")["light"] == 0.5
    assert m.mind.get("emotions")["joy"] == 0.5


def test_think_then_commit_appends() -> None:
    m = VConsciousness()
    v = m.mind.fork()
    m.think(v, "I see light")
    m.decide(v, "Open eyes")
    v.commit()
    assert m.thoughts() == ["I see light"]
    assert m.decision() == "Open eyes"


def test_think_then_abort_rolls_back() -> None:
    m = VConsciousness()
    v1 = m.mind.fork()
    m.think(v1, "first")
    v1.commit()

    v2 = m.mind.fork()
    m.think(v2, "second")
    v2.abort()
    assert m.thoughts() == ["first"]


def test_feel_updates_emotion_in_draft() -> None:
    m = VConsciousness()
    v = m.mind.fork()
    m.feel(v, "fear", 0.9)
    assert v.read("emotions")["fear"] == 0.9
    # Trunk should be untouched until commit.
    assert m.mind.get("emotions")["fear"] == 0.1
    v.commit()
    assert m.mind.get("emotions")["fear"] == 0.9


def test_decision_starts_none() -> None:
    m = VConsciousness()
    assert m.decision() is None


def test_regret_pattern() -> None:
    """A "regret" is a thought that never becomes a decision."""

    m = VConsciousness()
    v = m.mind.fork()
    m.think(v, "I want to scream")
    m.decide(v, "Scream")
    # ...but the actor reconsiders, aborts the decision.
    v.abort()
    assert m.decision() is None
    assert m.thoughts() == []


def test_custom_sensations_and_emotions() -> None:
    m = VConsciousness(
        sensations={"temperature": 0.7},
        emotions={"calm": 0.8},
    )
    assert m.mind.get("sensations") == {"temperature": 0.7}
    assert m.mind.get("emotions") == {"calm": 0.8}
