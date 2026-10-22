"""Tests for :class:`v_universal.math_layer.VMath`."""

from __future__ import annotations

import pytest

from v_universal.math_layer import VMath


def test_default_axioms_loaded() -> None:
    m = VMath()
    axioms = m.axioms.get("axioms")
    assert "refl" in axioms
    assert "sym" in axioms
    assert "trans" in axioms
    assert "add" in axioms


def test_prove_then_commit_adds_theorem() -> None:
    m = VMath()
    v = m.axioms.fork()
    m.prove(v, "a + 0 = a", ["add: a + 0 = a"])
    v.commit()
    assert m.has_theorem("a + 0 = a")
    assert m.proof_of("a + 0 = a") == ["add: a + 0 = a"]


def test_prove_then_abort_does_not_add() -> None:
    m = VMath()
    v = m.axioms.fork()
    m.prove(v, "0 + a = a", ["add: a + 0 = a", "sym: ...", "trans: ..."])
    v.abort()
    assert not m.has_theorem("0 + a = a")


def test_proof_of_unknown_raises() -> None:
    m = VMath()
    with pytest.raises(KeyError):
        m.proof_of("nonexistent")


def test_multiple_theorems_accumulate() -> None:
    m = VMath()
    v1 = m.axioms.fork()
    m.prove(v1, "t1", ["a1"])
    v1.commit()

    v2 = m.axioms.fork()
    m.prove(v2, "t2", ["a2"])
    v2.commit()

    assert m.has_theorem("t1")
    assert m.has_theorem("t2")


def test_custom_axioms() -> None:
    m = VMath(axioms={"my_axiom": "x = x"})
    assert "my_axiom" in m.axioms.get("axioms")
    assert "refl" not in m.axioms.get("axioms")
