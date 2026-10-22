"""V-HARDWARE — hardware transactional memory.

Models a tiny CPU with 16 registers, an address/data bus, and a 64-line
cache. ``begin_tx()`` forks all three layers; ``commit_tx()`` publishes
the writes atomically; ``abort_tx()`` rolls them back. This is the
classic HTM pattern, expressed in the same primitives as every other
domain in the library.
"""

from __future__ import annotations

from v_universal.core import VLayer, VVersion

_N_REGISTERS = 16
_CACHE_LINES = 64


class VHardware:
    """A 16-register CPU with a bus and a 64-line cache.

    The transactional memory abstraction is built directly on
    :class:`VLayer` / :class:`VVersion`: a "transaction" is just three
    simultaneous forks (one per layer), and commit/abort propagate to
    all three.
    """

    def __init__(self, n_registers: int = _N_REGISTERS, cache_lines: int = _CACHE_LINES) -> None:
        self.regs = VLayer("HW:Regs")
        for i in range(n_registers):
            self.regs.set_base(f"r{i}", 0)
        self.regs.crystallize()

        self.bus = VLayer("HW:Bus")
        self.bus.set_base("addr", 0)
        self.bus.set_base("data", 0)
        self.bus.set_base("rw", "read")
        self.bus.crystallize()

        self.cache = VLayer("HW:Cache")
        self.cache.set_base("lines", [None] * cache_lines)
        self.cache.crystallize()

        self.tx: dict[str, VVersion] | None = None

    # ----- transaction lifecycle -----------------------------------------

    def begin_tx(self) -> dict[str, VVersion]:
        """Open a transaction by forking all three layers."""

        if self.tx is not None:
            raise RuntimeError("transaction already in progress")
        self.tx = {
            "regs": self.regs.fork(),
            "bus": self.bus.fork(),
            "cache": self.cache.fork(),
        }
        return self.tx

    def commit_tx(self) -> None:
        """Atomically publish all pending writes to the trunk."""

        self._require_tx()
        for layer, ver in [
            (self.regs, self.tx["regs"]),
            (self.bus, self.tx["bus"]),
            (self.cache, self.tx["cache"]),
        ]:
            layer.commit(ver)
        self.tx = None

    def abort_tx(self) -> None:
        """Discard all pending writes from the current transaction."""

        self._require_tx()
        for ver in self.tx.values():
            ver.abort()
        self.tx = None

    # ----- per-layer accessors -------------------------------------------

    def write_reg(self, i: int, val: int) -> None:
        self._require_tx()
        if not 0 <= i < self._n_regs():
            raise IndexError(f"register index {i} out of range")
        self.tx["regs"].write(f"r{i}", val)

    def read_reg(self, i: int) -> int:
        self._require_tx()
        if not 0 <= i < self._n_regs():
            raise IndexError(f"register index {i} out of range")
        return self.tx["regs"].read(f"r{i}")

    def bus_write(self, addr: int, data: int) -> None:
        self._require_tx()
        self.tx["bus"].write("addr", addr)
        self.tx["bus"].write("data", data)
        self.tx["bus"].write("rw", "write")

    def bus_read(self, addr: int) -> int:
        """Stage a bus read and return the value at ``addr`` from the cache."""

        self._require_tx()
        self.tx["bus"].write("addr", addr)
        self.tx["bus"].write("rw", "read")
        lines = self.tx["cache"].read("lines")
        return lines[addr % len(lines)] if lines else None

    def cache_write(self, addr: int, data: int) -> None:
        self._require_tx()
        lines = list(self.tx["cache"].read("lines"))
        lines[addr % len(lines)] = data
        self.tx["cache"].write("lines", lines)

    def _n_regs(self) -> int:
        return len([k for k in self.regs._index if k.startswith("r")])  # noqa: SLF001

    def _require_tx(self) -> None:
        if self.tx is None:
            raise RuntimeError("no active transaction; call begin_tx() first")
