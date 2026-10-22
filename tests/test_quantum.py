"""Tests for :class:`v_universal.quantum.VQuantum`."""

from __future__ import annotations

import math

import numpy as np
import pytest

from v_universal.quantum import VQuantum, make_gate, nonzero_states, probabilities


def test_initial_state_is_zero() -> None:
    q = VQuantum(n_qubits=3)
    v = q.state.fork()
    vec = v.read("vec")
    assert vec[0] == 1.0
    assert np.allclose(vec[1:], 0.0)


def test_hadamard_creates_superposition() -> None:
    q = VQuantum(n_qubits=2)
    v = q.state.fork()
    q.apply_gate(v, make_gate("H"), 0)
    vec = v.read("vec")
    # |00> and |01> should each have amplitude 1/sqrt(2)
    assert math.isclose(abs(vec[0]), 1 / math.sqrt(2), abs_tol=1e-6)
    assert math.isclose(abs(vec[1]), 1 / math.sqrt(2), abs_tol=1e-6)
    assert np.allclose(vec[2:], 0.0)


def test_two_hadamards_give_four_states() -> None:
    q = VQuantum(n_qubits=2)
    v = q.state.fork()
    q.apply_gate(v, make_gate("H"), 0)
    q.apply_gate(v, make_gate("H"), 1)
    states = nonzero_states(v.read("vec"))
    assert sorted(states) == [0, 1, 2, 3]


def test_measurement_collapses_state() -> None:
    q = VQuantum(n_qubits=2)
    v = q.state.fork()
    q.apply_gate(v, make_gate("H"), 0)
    rng = np.random.default_rng(0)
    outcome = q.measure(v, rng=rng)
    vec = v.read("vec")
    # Only the sampled basis state should remain.
    expected = np.zeros_like(vec)
    expected[outcome] = 1.0
    assert np.allclose(vec, expected)


def test_pauli_x_flips_qubit() -> None:
    q = VQuantum(n_qubits=1)
    v = q.state.fork()
    q.apply_gate(v, make_gate("X"), 0)
    vec = v.read("vec")
    assert vec[0] == 0.0
    assert vec[1] == 1.0


def test_apply_gate_rejects_bad_shape() -> None:
    q = VQuantum(n_qubits=2)
    v = q.state.fork()
    with pytest.raises(ValueError):
        q.apply_gate(v, np.eye(4, dtype=complex), 0)


def test_apply_gate_rejects_bad_qubit() -> None:
    q = VQuantum(n_qubits=2)
    v = q.state.fork()
    with pytest.raises(IndexError):
        q.apply_gate(v, make_gate("H"), 5)


def test_cnot_entangles() -> None:
    q = VQuantum(n_qubits=2)
    v = q.state.fork()
    q.apply_gate(v, make_gate("X"), 0)  # |01>
    q.apply_cnot(v, control=0, target=1)
    vec = v.read("vec")
    # CNOT with control=0 (LSB) and target=1 should flip target when control=1.
    expected = np.zeros_like(vec)
    expected[0b11] = 1.0
    assert np.allclose(vec, expected)


def test_cnot_rejects_same_control_target() -> None:
    q = VQuantum(n_qubits=2)
    v = q.state.fork()
    with pytest.raises(ValueError):
        q.apply_cnot(v, control=0, target=0)


def test_measure_rejects_zero_norm() -> None:
    q = VQuantum(n_qubits=1)
    v = q.state.fork()
    v.write("vec", np.zeros(2, dtype=complex))
    with pytest.raises(RuntimeError):
        q.measure(v)


def test_make_gate_unknown() -> None:
    with pytest.raises(KeyError):
        make_gate("Y")


def test_probabilities_normalises() -> None:
    vec = np.array([1.0, 2.0, 3.0, 4.0], dtype=complex)
    p = probabilities(vec)
    assert math.isclose(p.sum(), 1.0)
