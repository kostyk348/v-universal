"""V-QUANTUM — quantum state as a versioned trunk.

The state vector is the trunk; gate applications are versions;
measurement is a commit (the trunk collapses to a basis state);
``fork + abort`` models a "what-if" branch that decays back into the
trunk state without affecting it.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

from v_universal.core import VLayer, VVersion


class VQuantum:
    """A toy ``n``-qubit state vector wrapped in a :class:`VLayer`.

    Only single-qubit gates are supported. Measurement collapses the
    state to a single computational-basis vector and returns the index.
    """

    def __init__(self, n_qubits: int = 4) -> None:
        if n_qubits <= 0:
            raise ValueError("n_qubits must be positive")
        self.n = n_qubits
        self.dim = 1 << n_qubits
        self.state = VLayer("Q:State")

        vec = np.zeros(self.dim, dtype=complex)
        vec[0] = 1.0
        self.state.set_base("vec", vec)
        self.state.set_base("n", n_qubits)
        self.state.crystallize()

    def apply_gate(self, version: VVersion, gate: np.ndarray, qubit: int) -> None:
        """Apply a single-qubit ``gate`` to ``qubit`` within ``version``.

        ``gate`` must be a 2x2 complex matrix. ``qubit`` is 0-indexed;
        qubit 0 is the *least* significant bit of the basis index, in
        line with the convention used by most quantum-computing
        libraries.
        """

        if gate.shape != (2, 2):
            raise ValueError(f"gate must be 2x2, got {gate.shape}")
        if not 0 <= qubit < self.n:
            raise IndexError(f"qubit {qubit} out of range [0, {self.n})")

        vec = version.read("vec").copy()
        new = np.zeros_like(vec)
        for i in range(self.dim):
            bit = (i >> qubit) & 1
            j = i ^ (1 << qubit)
            if bit == 0:
                new[i] += gate[0, 0] * vec[i] + gate[0, 1] * vec[j]
            else:
                new[i] += gate[1, 0] * vec[j] + gate[1, 1] * vec[i]
        version.write("vec", new)

    def apply_cnot(self, version: VVersion, control: int, target: int) -> None:
        """Apply a CNOT gate with ``control`` and ``target`` qubits."""

        if control == target:
            raise ValueError("control and target must differ")
        vec = version.read("vec").copy()
        new = np.zeros_like(vec)
        for i in range(self.dim):
            if (i >> control) & 1:
                j = i ^ (1 << target)
                new[i] = vec[j]
            else:
                new[i] = vec[i]
        version.write("vec", new)

    def measure(self, version: VVersion, rng: np.random.Generator | None = None) -> int:
        """Collapse ``version`` to a single basis state.

        Returns the index of the sampled basis state.
        """

        rng = rng or np.random.default_rng()
        vec = version.read("vec")
        probs = np.abs(vec) ** 2
        total = probs.sum()
        if total == 0:
            raise RuntimeError("state vector has zero norm")
        probs = probs / total
        outcome = int(rng.choice(self.dim, p=probs))
        new = np.zeros_like(vec)
        new[outcome] = 1.0
        version.write("vec", new)
        return outcome

    @staticmethod
    def hadamard() -> np.ndarray:
        return np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)

    @staticmethod
    def pauli_x() -> np.ndarray:
        return np.array([[0, 1], [1, 0]], dtype=complex)

    @staticmethod
    def pauli_z() -> np.ndarray:
        return np.array([[1, 0], [0, -1]], dtype=complex)

    @staticmethod
    def identity() -> np.ndarray:
        return np.eye(2, dtype=complex)


def make_gate(gate: str = "H") -> np.ndarray:
    """Convenience constructor for the most common single-qubit gates."""

    gates = {
        "H": VQuantum.hadamard(),
        "X": VQuantum.pauli_x(),
        "Z": VQuantum.pauli_z(),
        "I": VQuantum.identity(),
    }
    if gate not in gates:
        raise KeyError(f"unknown gate {gate!r}; choose one of {list(gates)}")
    return gates[gate]


def probabilities(vec: np.ndarray) -> np.ndarray:
    """Return ``|vec|^2`` normalised to sum to 1."""

    p = np.abs(vec) ** 2
    total = p.sum()
    if total == 0:
        raise RuntimeError("zero-norm state vector")
    return p / total


def nonzero_states(vec: np.ndarray, tol: float = 1e-9) -> Sequence[int]:
    """Return the indices of basis states with non-trivial probability."""

    p = probabilities(vec)
    return [int(i) for i in np.nonzero(p > tol)[0]]
