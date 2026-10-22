"""Tests for :class:`v_universal.hardware.VHardware`."""

from __future__ import annotations

import pytest

from v_universal.hardware import VHardware


def test_begin_then_abort_rolls_back() -> None:
    hw = VHardware()
    hw.begin_tx()
    hw.write_reg(0, 42)
    hw.write_reg(1, 100)
    hw.bus_write(0x1000, 0xDEAD)
    assert hw.read_reg(0) == 42
    hw.abort_tx()
    assert hw.regs.get("r0") == 0
    assert hw.bus.get("addr") == 0
    assert hw.bus.get("data") == 0


def test_begin_then_commit_persists() -> None:
    hw = VHardware()
    hw.begin_tx()
    hw.write_reg(0, 42)
    hw.commit_tx()
    assert hw.regs.get("r0") == 42


def test_double_begin_raises() -> None:
    hw = VHardware()
    hw.begin_tx()
    with pytest.raises(RuntimeError):
        hw.begin_tx()


def test_ops_without_tx_raise() -> None:
    hw = VHardware()
    with pytest.raises(RuntimeError):
        hw.write_reg(0, 1)
    with pytest.raises(RuntimeError):
        hw.read_reg(0)
    with pytest.raises(RuntimeError):
        hw.commit_tx()
    with pytest.raises(RuntimeError):
        hw.abort_tx()


def test_register_out_of_range_raises() -> None:
    hw = VHardware()
    hw.begin_tx()
    with pytest.raises(IndexError):
        hw.write_reg(99, 1)
    with pytest.raises(IndexError):
        hw.read_reg(-1)


def test_cache_round_trip_in_tx() -> None:
    hw = VHardware()
    hw.begin_tx()
    hw.cache_write(5, 0xBEEF)
    assert hw.bus_read(5) == 0xBEEF
    hw.commit_tx()
    # Trunk now holds the updated cache line.
    assert hw.cache.get("lines")[5] == 0xBEEF


def test_bus_write_updates_rw_flag() -> None:
    hw = VHardware()
    hw.begin_tx()
    hw.bus_write(0x10, 0xABCD)
    assert hw.tx["bus"].read("rw") == "write"
    hw.abort_tx()


def test_custom_dimensions() -> None:
    hw = VHardware(n_registers=8, cache_lines=16)
    assert len(hw.cache.get("lines")) == 16
    hw.begin_tx()
    hw.write_reg(7, 123)
    assert hw.read_reg(7) == 123
    hw.commit_tx()
