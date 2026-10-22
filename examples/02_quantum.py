"""02 — V-QUANTUM: state vector as a versioned trunk."""

from __future__ import annotations

import numpy as np

from v_universal import VQuantum
from v_universal.quantum import nonzero_states


def main() -> None:
    print("=== V-QUANTUM: quantum states as versions ===")
    q = VQuantum(n_qubits=4)

    # Apply Hadamard on qubit 0, then on qubit 1 — should produce 4-state superposition.
    v = q.state.fork()
    q.apply_gate(v, q.hadamard(), 0)
    print(
        "after H on qubit 0:",
        f"|0000> amp = {v.read('vec')[0]:.3f}",
        f"|0001> amp = {v.read('vec')[1]:.3f}",
    )
    q.apply_gate(v, q.hadamard(), 1)
    print(f"after H on qubit 1: {len(nonzero_states(v.read('vec')))} non-zero states")

    # Measurement collapses to one basis state.
    rng = np.random.default_rng(0)
    outcome = q.measure(v, rng=rng)
    print(f"measured: |{outcome:04b}>")
    v.commit()
    committed = int(np.argmax(np.abs(q.state.get("vec"))))
    print(f"committed state: |{committed:04b}>")

    # Fork + abort: probe a branch without disturbing the trunk.
    v2 = q.state.fork()
    print(f"branch state: |{int(np.argmax(np.abs(v2.read('vec')))):04b}>")
    v2.abort()


if __name__ == "__main__":
    main()
