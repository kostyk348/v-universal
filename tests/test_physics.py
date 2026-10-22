"""Tests for :class:`v_universal.physics.VPhysics`."""

from __future__ import annotations

import pytest

from v_universal.physics import VPhysics


def test_default_constants() -> None:
    phy = VPhysics()
    assert phy.laws.get("G") == 9.81
    assert phy.laws.get("dt") == 0.01
    assert phy.laws.get("damping") == 0.99


def test_add_body_then_step_advances_position() -> None:
    phy = VPhysics(gravity=0.0, dt=0.1, damping=1.0)
    v = phy.world.fork()
    phy.add_body(v, pos=(0.0, 0.0), vel=(1.0, 0.0))
    phy.run(v, 10)
    x, y = VPhysics.position_of(v)
    assert x == pytest.approx(1.0, abs=1e-6)
    assert y == pytest.approx(0.0, abs=1e-6)


def test_gravity_pulls_down() -> None:
    phy = VPhysics(gravity=9.81, dt=0.1, damping=1.0)
    v = phy.world.fork()
    phy.add_body(v, pos=(0.0, 100.0), vel=(0.0, 0.0))
    phy.run(v, 10)
    _, y = VPhysics.position_of(v)
    # After 10 steps of dt=0.1, gravity pulls the body down: Δy = -0.5 * g * t^2 = -0.4905
    assert y < 100.0


def test_multiverse_branches_do_not_pollute_trunk() -> None:
    phy = VPhysics()
    base_bodies = phy.world.get("bodies")
    assert base_bodies == []

    for _ in range(3):
        v = phy.world.fork()
        phy.add_body(v, pos=(0.0, 0.0), vel=(1.0, 0.0))
        phy.run(v, 5)
        v.abort()

    assert phy.world.get("bodies") == []


def test_position_of_rejects_empty_world() -> None:
    phy = VPhysics()
    v = phy.world.fork()
    with pytest.raises(IndexError):
        VPhysics.position_of(v)


def test_position_of_rejects_bad_index() -> None:
    phy = VPhysics()
    v = phy.world.fork()
    phy.add_body(v, pos=(0.0, 0.0), vel=(0.0, 0.0))
    with pytest.raises(IndexError):
        VPhysics.position_of(v, body_index=5)


def test_run_rejects_negative_steps() -> None:
    phy = VPhysics()
    v = phy.world.fork()
    with pytest.raises(ValueError):
        phy.run(v, -1)


def test_world_inherits_laws() -> None:
    phy = VPhysics(gravity=1.62, dt=0.5, damping=0.9)
    v = phy.world.fork()
    # Reading a law through the world layer should hit the base layer.
    assert v.read("G") == 1.62
    assert v.read("dt") == 0.5
    assert v.read("damping") == 0.9


def test_override_law_in_branch() -> None:
    """A fork can locally override a law without touching the trunk."""

    phy = VPhysics(gravity=9.81)
    v = phy.world.fork()
    v.write("G", 1.62)  # moon gravity in this branch only
    assert v.read("G") == 1.62
    assert phy.laws.get("G") == 9.81  # trunk unchanged
    v.abort()
