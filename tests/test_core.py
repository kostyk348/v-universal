"""Tests for the core :class:`Version` / :class:`VLayer` / :class:`VVersion`."""

from __future__ import annotations

import pytest

from v_universal.core import Version, VLayer


def test_version_chain_depth_increments() -> None:
    root = Version(parent=None, changes={"a": 1})
    child = Version(parent=root, changes={"b": 2})
    grandchild = Version(parent=child, changes={"c": 3})
    assert root.depth == 0
    assert child.depth == 1
    assert grandchild.depth == 2
    assert root in child.children or child in root.children


def test_version_ids_are_unique() -> None:
    a = Version(parent=None, changes={})
    b = Version(parent=None, changes={})
    assert a.id != b.id


def test_set_base_rejects_after_crystallize() -> None:
    layer = VLayer("X")
    layer.set_base("k", "v")
    layer.crystallize()
    with pytest.raises(RuntimeError):
        layer.set_base("k2", "v2")


def test_get_returns_default() -> None:
    layer = VLayer("X")
    layer.set_base("k", "v")
    assert layer.get("missing") is None
    assert layer.get("missing", "fallback") == "fallback"


def test_fork_does_not_mutate_trunk() -> None:
    layer = VLayer("X")
    layer.set_base("k", 1)
    layer.crystallize()

    v = layer.fork()
    v.write("k", 99)
    assert layer.get("k") == 1, "trunk must not change before commit"
    assert v.read("k") == 99


def test_commit_publishes_to_trunk() -> None:
    layer = VLayer("X")
    layer.set_base("k", 1)
    layer.crystallize()

    v = layer.fork()
    v.write("k", 42)
    v.write("new", "value")
    v.commit()

    assert layer.get("k") == 42
    assert layer.get("new") == "value"
    assert layer.version_count == 2  # crystallize + commit


def test_abort_discards_draft() -> None:
    layer = VLayer("X")
    layer.set_base("k", 1)
    layer.crystallize()

    v = layer.fork()
    v.write("k", 99)
    v.abort()
    assert v.read("k") == 1
    assert layer.get("k") == 1


def test_read_walks_version_chain() -> None:
    layer = VLayer("X")
    layer.set_base("k", "trunk")
    layer.set_base("other", "trunk")
    layer.crystallize()

    v1 = layer.fork()
    v1.write("k", "v1")
    v1.commit()

    v2 = layer.fork()
    v2.write("other", "v2")

    # ``k`` should resolve from the committed trunk; ``other`` from the draft.
    assert v2.read("k") == "v1"
    assert v2.read("other") == "v2"


def test_base_layer_inheritance() -> None:
    base = VLayer("Base")
    base.set_base("shared", "from_base")
    base.crystallize()

    child = VLayer("Child", base=base)
    child.set_base("own", "from_child")
    child.crystallize()

    v = child.fork()
    assert v.read("shared") == "from_base"
    assert v.read("own") == "from_child"
    assert v.read("missing", "default") == "default"


def test_multiple_forks_are_independent() -> None:
    layer = VLayer("X")
    layer.set_base("k", 0)
    layer.crystallize()

    a = layer.fork()
    b = layer.fork()
    a.write("k", 1)
    b.write("k", 2)
    assert a.read("k") == 1
    assert b.read("k") == 2
    assert layer.get("k") == 0
