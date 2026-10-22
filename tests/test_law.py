"""Tests for :class:`v_universal.law.VLaw`."""

from __future__ import annotations

import pytest

from v_universal.law import VLaw


def test_default_articles() -> None:
    law = VLaw()
    articles = law.articles()
    assert "art1" in articles
    assert "art2" in articles
    assert "art3" in articles


def test_propose_law_then_commit() -> None:
    law = VLaw()
    v = law.const.fork()
    law.propose_law(v, "law_1", "Flat tax 13%")
    v.commit()
    assert law.has_law("law_1")
    assert law.law_text("law_1") == "Flat tax 13%"


def test_propose_law_then_abort() -> None:
    law = VLaw()
    v = law.const.fork()
    law.propose_law(v, "law_1", "Should not persist")
    v.abort()
    assert not law.has_law("law_1")


def test_amend_constitution() -> None:
    law = VLaw()
    v = law.const.fork()
    law.amend_constitution(v, "art4", "Right to education")
    v.commit()
    assert "art4" in law.articles()
    assert law.articles()["art4"] == "Right to education"


def test_law_text_unknown_raises() -> None:
    law = VLaw()
    with pytest.raises(KeyError):
        law.law_text("nonexistent")


def test_custom_articles() -> None:
    law = VLaw(articles={"artX": "Custom article"})
    assert "artX" in law.articles()
    assert "art1" not in law.articles()


def test_overlapping_laws_in_forks() -> None:
    law = VLaw()
    a = law.const.fork()
    b = law.const.fork()
    law.propose_law(a, "tax", "13%")
    law.propose_law(b, "tax", "20%")
    a.commit()
    b.commit()  # overwrites the trunk's "tax"
    assert law.law_text("tax") == "20%"
