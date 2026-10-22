"""Tests for :class:`v_universal.economy.VEconomy`."""

from __future__ import annotations

import pytest

from v_universal.economy import InsufficientFunds, VEconomy


def test_default_accounts() -> None:
    eco = VEconomy()
    assert eco.balance("alice") == 1000.0
    assert eco.balance("bob") == 500.0
    assert eco.balance("carol") == 0.0


def test_transfer_then_commit() -> None:
    eco = VEconomy()
    v = eco.ledger.fork()
    eco.transfer(v, "alice", "bob", 100)
    v.commit()
    assert eco.balance("alice") == 900
    assert eco.balance("bob") == 600


def test_transfer_then_abort_rolls_back() -> None:
    eco = VEconomy()
    v = eco.ledger.fork()
    eco.transfer(v, "alice", "bob", 100)
    v.abort()
    assert eco.balance("alice") == 1000
    assert eco.balance("bob") == 500


def test_insufficient_funds_raises_and_is_rolled_back() -> None:
    eco = VEconomy()
    v = eco.ledger.fork()
    with pytest.raises(InsufficientFunds):
        eco.transfer(v, "carol", "alice", 10000)
    v.abort()
    assert eco.balance("carol") == 0
    assert eco.balance("alice") == 1000


def test_zero_or_negative_amount_rejected() -> None:
    eco = VEconomy()
    v = eco.ledger.fork()
    with pytest.raises(ValueError):
        eco.transfer(v, "alice", "bob", 0)
    with pytest.raises(ValueError):
        eco.transfer(v, "alice", "bob", -1)


def test_total_supply_is_conserved() -> None:
    eco = VEconomy()
    initial = eco.total_supply()
    v = eco.ledger.fork()
    eco.transfer(v, "alice", "bob", 300)
    eco.transfer(v, "bob", "carol", 50)
    v.commit()
    assert eco.total_supply() == initial


def test_custom_accounts() -> None:
    eco = VEconomy(accounts={"x": 10, "y": 20})
    assert eco.balance("x") == 10
    assert eco.balance("y") == 20
    with pytest.raises(KeyError):
        eco.balance("alice")


def test_negative_initial_balance_rejected() -> None:
    with pytest.raises(ValueError):
        VEconomy(accounts={"broke": -5})


def test_non_numeric_balance_rejected() -> None:
    with pytest.raises(TypeError):
        VEconomy(accounts={"x": "rich"})


def test_parallel_branches_are_independent() -> None:
    eco = VEconomy()
    a = eco.ledger.fork()
    b = eco.ledger.fork()
    eco.transfer(a, "alice", "bob", 50)
    eco.transfer(b, "alice", "carol", 300)
    # Both branches see the *initial* alice balance, not each other's writes.
    assert a.read("accounts")["alice"] == 950
    assert b.read("accounts")["alice"] == 700
