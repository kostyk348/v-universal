"""05 — V-MATH: axioms as trunk, theorems as versions."""

from __future__ import annotations

from v_universal import VMath


def main() -> None:
    print("=== V-MATH: axioms as trunk, theorems as versions ===")
    m = VMath()
    print(f"axioms: {list(m.axioms.get('axioms').keys())}")

    v1 = m.axioms.fork()
    m.prove(v1, "a + 0 = a", ["add: a + 0 = a"])
    v1.commit()
    print(f"committed theorem: {list(m.axioms.get('theorems').keys())}")

    v2 = m.axioms.fork()
    m.prove(
        v2,
        "0 + a = a",
        ["add: a + 0 = a", "sym: 0 + a = a + 0", "trans: 0 + a = a"],
    )
    v2.commit()
    print(f"committed theorem: {list(m.axioms.get('theorems').keys())}")

    # A failed proof that we abort.
    v3 = m.axioms.fork()
    m.prove(v3, "1 = 2", ["faulty step"])
    print(f"branch theorem (will be aborted): {list(v3.read('theorems').keys())}")
    v3.abort()
    print(f"after abort: trunk theorems = {list(m.axioms.get('theorems').keys())}")


if __name__ == "__main__":
    main()
