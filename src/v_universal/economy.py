"""V-ECONOMY — ledger as trunk, transfers as versions.

A toy ledger with named accounts. A transfer is a fork: stage the
debit/credit into the draft, and either commit (transaction is
settled) or abort (rolled back, e.g. because of insufficient funds).
"""

from __future__ import annotations

from v_universal.core import VLayer, VVersion


class InsufficientFunds(ValueError):
    """Raised by :meth:`VEconomy.transfer` when the sender is too poor."""


class VEconomy:
    """A simple account ledger wrapped in a :class:`VLayer`."""

    def __init__(self, accounts: dict[str, float] | None = None) -> None:
        if accounts is not None:
            for name, bal in accounts.items():
                if not isinstance(bal, int | float):
                    raise TypeError(f"account balance must be numeric, got {type(bal)}")
                if bal < 0:
                    raise ValueError(f"account {name!r} starts negative: {bal}")
        initial = dict(accounts or {"alice": 1000.0, "bob": 500.0, "carol": 0.0})
        self.ledger = VLayer("ECO:Ledger")
        self.ledger.set_base("accounts", initial)
        self.ledger.crystallize()

    def transfer(self, version: VVersion, frm: str, to: str, amount: float) -> None:
        """Stage a transfer ``frm -> to`` of ``amount`` into ``version``.

        Raises
        ------
        ValueError
            If ``amount`` is not positive.
        :class:`InsufficientFunds`
            If the sender does not have enough balance.
        """

        if amount <= 0:
            raise ValueError("transfer amount must be positive")
        accounts = dict(version.read("accounts"))
        if accounts.get(frm, 0) < amount:
            raise InsufficientFunds(f"{frm} has {accounts.get(frm, 0)}, cannot send {amount}")
        accounts[frm] = accounts.get(frm, 0) - amount
        accounts[to] = accounts.get(to, 0) + amount
        version.write("accounts", accounts)

    def balance(self, name: str) -> float:
        accounts: dict = self.ledger.get("accounts")
        if name not in accounts:
            raise KeyError(f"no such account: {name!r}")
        return float(accounts[name])

    def total_supply(self) -> float:
        """Return the sum of all account balances."""

        accounts: dict = self.ledger.get("accounts")
        return float(sum(accounts.values()))
