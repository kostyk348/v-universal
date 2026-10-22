"""Tests for :mod:`v_universal.benchmark`."""

from __future__ import annotations

import pytest

from v_universal.benchmark import bench_universal, format_results


def test_bench_universal_returns_four_domains() -> None:
    results = bench_universal(n=100)
    assert set(results.keys()) == {
        "V-HARDWARE",
        "V-BIO",
        "V-ECONOMY",
        "V-CONSCIOUSNESS",
    }


def test_bench_universal_times_are_positive() -> None:
    results = bench_universal(n=10)
    for name, t in results.items():
        assert t >= 0, f"{name} took negative time: {t}"


def test_bench_universal_rejects_non_positive_n() -> None:
    with pytest.raises(ValueError):
        bench_universal(n=0)
    with pytest.raises(ValueError):
        bench_universal(n=-1)


def test_format_results_returns_table() -> None:
    results = {"V-X": 0.1, "V-Y": 0.2}
    out = format_results(results, n=100)
    assert "V-X" in out
    assert "V-Y" in out
    assert "domain" in out  # header row
