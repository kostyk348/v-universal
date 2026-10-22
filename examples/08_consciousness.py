"""08 — V-CONSCIOUSNESS: sensations as trunk, thoughts as versions."""

from __future__ import annotations

from v_universal import VConsciousness


def main() -> None:
    print("=== V-CONSCIOUSNESS: sensations as trunk, thoughts as versions ===")
    m = VConsciousness()
    print(f"sensations: {m.mind.get('sensations')}")
    print(f"emotions:   {m.mind.get('emotions')}")

    # Thought + decision + commit.
    v1 = m.mind.fork()
    m.think(v1, "I see light")
    m.decide(v1, "Open eyes")
    v1.commit()
    print(f"after commit: thoughts={m.thoughts()}, decision={m.decision()!r}")

    # Another thought.
    v2 = m.mind.fork()
    m.think(v2, "I feel pain")
    m.decide(v2, "Pull hand back")
    v2.commit()
    print(f"after commit: thoughts={m.thoughts()}")

    # Regret: a thought that happens but does not become a decision.
    v3 = m.mind.fork()
    m.think(v3, "I want to scream")
    m.decide(v3, "Scream")
    print(f"branch decision: {v3.read('decision')!r}")
    v3.abort()
    print(f"after abort: decision={m.decision()!r} (regret)")


if __name__ == "__main__":
    main()
