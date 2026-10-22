"""Core versioning primitives.

The whole library is built on three classes:

* :class:`Version` — an immutable node in a version tree. Each node
  holds a ``changes`` dict relative to its parent. Walking the chain
  ``version → parent → parent → …`` recovers the full state visible at
  that node.
* :class:`VLayer` — the *trunk*. A layer owns a root version, the
  current head, a flat index of last-writer-wins values, and an
  optional base layer for inheritance. ``crystallize()`` marks the
  trunk as no-longer-mutable so further ``set_base`` calls raise.
* :class:`VVersion` — a *cheap fork* of a layer. Writes go into an
  in-memory ``draft`` dict. ``commit()`` publishes the draft back into
  the trunk; ``abort()`` discards it.

The point of the design: every domain in :mod:`v_universal` reuses the
same three primitives. Forking a genome, a quantum state, a physical
world, or a bank account is literally the same operation under the hood.
"""

from __future__ import annotations

from typing import Any


class Version:
    """A single immutable node in the version tree.

    Attributes
    ----------
    parent:
        Parent node, or ``None`` for the root.
    changes:
        Dict of values introduced *at this node*. Reading a key walks
        up the parent chain until the key is found.
    depth:
        Distance from the root. Useful for diagnostics and for
        balancing the tree.
    id:
        Monotonically increasing id, unique within the Python process.
    children:
        List of versions that were committed on top of this one. Useful
        for visualisation; not used by the resolution algorithm.
    """

    __slots__ = ("parent", "changes", "depth", "id", "children")
    _counter: int = 0

    def __init__(self, parent: Version | None, changes: dict[str, Any]) -> None:
        self.parent = parent
        self.changes = changes
        self.depth = (parent.depth + 1) if parent is not None else 0
        Version._counter += 1
        self.id = Version._counter
        self.children: list[Version] = []
        if parent is not None:
            parent.children.append(self)

    def __repr__(self) -> str:  # pragma: no cover — debugging only
        return f"Version(id={self.id}, depth={self.depth}, keys={list(self.changes)})"


class VLayer:
    """A versioned trunk.

    A layer is "crystallised" once any forks have been created from it.
    After crystallisation, ``set_base`` raises — base values must be
    defined up-front, before any forking happens.

    A layer may declare a ``base`` layer. ``resolve`` walks up the
    version chain first, then falls back to the layer's own flat index,
    and finally asks the base layer. This lets us compose layers (e.g.
    a Physics world that inherits constants from a Physics laws layer).
    """

    def __init__(self, name: str, base: VLayer | None = None) -> None:
        self.name = name
        self.base = base
        self.root = Version(parent=None, changes={})
        self.head: Version = self.root
        self._index: dict[str, Any] = {}
        self.version_count: int = 0

    def __repr__(self) -> str:  # pragma: no cover — debugging only
        return f"VLayer(name={self.name!r}, versions={self.version_count})"

    def set_base(self, key: str, val: Any) -> None:
        """Define an initial value at the root.

        Raises
        ------
        RuntimeError
            If any forks have already been created from this layer.
        """

        if self.version_count > 0:
            raise RuntimeError(f"{self.name} already crystallised")
        self.root.changes[key] = val
        self._index[key] = val

    def get(self, key: str, default: Any = None) -> Any:
        """Return the last-committed value for ``key``.

        This is a fast lookup against the flat index; it does not walk
        the version tree. Use :meth:`VVersion.read` for tree-aware
        reads inside an uncommitted fork.
        """

        return self._index.get(key, default)

    def crystallize(self) -> None:
        """Mark this layer as frozen for ``set_base`` purposes."""

        self.version_count += 1

    def fork(self) -> VVersion:
        """Create a cheap in-memory fork of the current head."""

        return VVersion(self)

    def commit(self, version: VVersion) -> Version:
        """Publish ``version.draft`` into the trunk.

        Creates a new :class:`Version` node, updates ``self.head``,
        writes all draft values into the flat index, and returns the
        new node.
        """

        v = Version(parent=version.base_version, changes=dict(version.draft))
        self.head = v
        for k, val in version.draft.items():
            self._index[k] = val
        self.version_count += 1
        return v

    def resolve(self, version: Version, key: str, default: Any = None) -> Any:
        """Walk the version chain for ``key``.

        Used by :meth:`VVersion.read` to resolve keys that have not been
        written into the current draft. Falls back to the flat index,
        then to the base layer if one was configured.
        """

        v = version
        while v is not None:
            if key in v.changes:
                return v.changes[key]
            v = v.parent
        if key in self._index:
            return self._index[key]
        if self.base is not None:
            return self.base.resolve(self.base.head, key, default)
        return default


class VVersion:
    """A cheap in-memory fork of a :class:`VLayer`.

    Writes go into ``self.draft``. Reads first check the draft, then
    delegate to :meth:`VLayer.resolve` against the version that was
    head when the fork was created (so concurrent commits to the trunk
    are *not* visible to this fork).

    Call :meth:`commit` to publish the draft back to the trunk, or
    :meth:`abort` to throw it away.
    """

    __slots__ = ("layer", "base_version", "draft")

    def __init__(self, layer: VLayer) -> None:
        self.layer = layer
        self.base_version = layer.head
        self.draft: dict[str, Any] = {}

    def write(self, key: str, val: Any) -> None:
        """Stage a write into the draft."""

        self.draft[key] = val

    def read(self, key: str, default: Any = None) -> Any:
        """Read a key, checking the draft first then walking the tree."""

        if key in self.draft:
            return self.draft[key]
        return self.layer.resolve(self.base_version, key, default)

    def abort(self) -> None:
        """Discard the draft."""

        self.draft.clear()

    def commit(self) -> Version:
        """Publish the draft into the trunk and return the new node."""

        return self.layer.commit(self)
