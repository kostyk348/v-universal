"""07 — V-ECONOMY: ledger as trunk, transfers as versions."""

from __future__ import annotations

from v_universal import VEconomy
from v_universal.economy import InsufficientFunds


def main() -> None:
    print("=== V-ECONOMY: ledger as trunk, transfers as versions ===")
    eco = VEconomy()
    print(f"initial: {eco.ledger.get('accounts')}")

    # Successful transfer.
    v1 = eco.ledger.fork()
    eco.transfer(v1, "alice", "bob", 100)
    v1.commit()
    print(f"after tx1 (alice -> bob 100): {eco.ledger.get('accounts')}")

    v2 = eco.ledger.fork()
    eco.transfer(v2, "bob", "carol", 200)
    v2.commit()
    print(f"after tx2 (bob -> carol 200): {eco.ledger.get('accounts')}")

    # Failed transfer (insufficient funds).
    v3 = eco.ledger.fork()
    try:
        eco.transfer(v3, "carol", "alice", 10000)
        v3.commit()
    except InsufficientFunds as e:
        print(f"tx3 failed: {e}")
        v3.abort()
    print(f"after failed tx3: {eco.ledger.get('accounts')}")

    # Multiverse: parallel transfers from the same base state.
    print("multiverse: parallel transfers from one state")
    for frm, to, amt in [("alice", "bob", 50), ("bob", "carol", 100), ("alice", "carol", 300)]:
        v = eco.ledger.fork()
        try:
            eco.transfer(v, frm, to, amt)
            print(f"  branch {frm}->{to} {amt}: {v.read('accounts')}")
        except InsufficientFunds as e:
            print(f"  branch {frm}->{to} {amt} failed: {e}")
        v.abort()


if __name__ == "__main__":
    main()
