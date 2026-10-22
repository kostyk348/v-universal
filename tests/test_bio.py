"""Tests for :class:`v_universal.bio.VBio`."""

from __future__ import annotations

import pytest

from v_universal.bio import VBio, _gc_content


def test_default_genome_size() -> None:
    bio = VBio(genome_size=32, seed=0)
    assert len(bio.genome.get("seq")) == 32
    assert all(c in "ACGT" for c in bio.genome.get("seq"))


def test_mutate_changes_at_least_one_base_at_high_rate() -> None:
    bio = VBio(genome_size=64, seed=1)
    v = bio.genome.fork()
    n = bio.mutate(v, rate=1.0)
    assert n == 64
    # All bases should differ from the trunk with overwhelming probability.
    trunk = bio.genome.get("seq")
    forked = v.read("seq")
    assert trunk != forked


def test_mutate_rate_zero_is_noop() -> None:
    bio = VBio(genome_size=64, seed=2)
    v = bio.genome.fork()
    n = bio.mutate(v, rate=0.0)
    assert n == 0
    assert v.read("seq") == bio.genome.get("seq")


def test_mutate_rejects_bad_rate() -> None:
    bio = VBio()
    v = bio.genome.fork()
    with pytest.raises(ValueError):
        bio.mutate(v, rate=-0.1)
    with pytest.raises(ValueError):
        bio.mutate(v, rate=1.5)


def test_evaluate_default_is_gc_content() -> None:
    bio = VBio(genome_size=10, seed=3)
    v = bio.genome.fork()
    v.write("seq", list("GGGGCCCCCC"))
    score = bio.evaluate(v)
    assert score == 1.0


def test_evaluate_custom_fitness() -> None:
    bio = VBio(genome_size=4, seed=4)
    v = bio.genome.fork()
    v.write("seq", list("ATAT"))
    # Custom fitness: count of A's
    score = bio.evaluate(v, fitness=lambda s: sum(1 for c in s if c == "A"))
    assert score == 2.0


def test_select_returns_top_k() -> None:
    bio = VBio(genome_size=8, seed=5)
    pop = []
    for gc_target in [0.0, 0.5, 1.0]:
        v = bio.genome.fork()
        v.write("seq", ["G" if i < int(gc_target * 8) else "A" for i in range(8)])
        bio.evaluate(v)
        pop.append(v)

    top = bio.select(pop, k=2)
    assert top[0].read("fitness") == 1.0
    assert top[1].read("fitness") == 0.5


def test_select_rejects_empty() -> None:
    bio = VBio()
    with pytest.raises(ValueError):
        bio.select([], k=1)


def test_select_rejects_bad_k() -> None:
    bio = VBio()
    v = bio.genome.fork()
    with pytest.raises(ValueError):
        bio.select([v], k=2)


def test_commit_persists_best_genome() -> None:
    bio = VBio(genome_size=8, seed=6)
    v = bio.genome.fork()
    v.write("seq", list("GGGGCCCC"))
    v.commit()
    assert bio.genome.get("seq") == list("GGGGCCCC")


def test_private_gc_content_helper() -> None:
    assert _gc_content(list("GCAT")) == 0.5
    assert _gc_content([]) == 0.0


def test_genome_size_must_be_positive() -> None:
    with pytest.raises(ValueError):
        VBio(genome_size=0)
