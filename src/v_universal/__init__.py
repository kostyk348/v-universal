"""V-UNIVERSAL — one versioning model for everything.

A tiny library that applies the same *trunk + version-tree* abstraction
to nine different domains. The trunk is a `VLayer` holding the canonical
state; a `VVersion` is a cheap in-memory fork of that trunk. Writes go
to the version's draft, `commit()` pushes them back into the trunk,
`abort()` throws them away.

This lets us treat — with the same three primitives ``fork / write /
commit`` — hardware transactional memory, quantum state vectors, a
genetic population, a physical multiverse, an axiomatic system, a legal
code, a financial ledger, and a stream of consciousness.

Each domain lives in its own module:

* :mod:`v_universal.core`           — Version, VLayer, VVersion
* :mod:`v_universal.hardware`       — VHardware (HTM)
* :mod:`v_universal.quantum`        — VQuantum
* :mod:`v_universal.bio`            — VBio
* :mod:`v_universal.physics`        — VPhysics
* :mod:`v_universal.math_layer`     — VMath
* :mod:`v_universal.law`            — VLaw
* :mod:`v_universal.economy`        — VEconomy
* :mod:`v_universal.consciousness`  — VConsciousness
* :mod:`v_universal.benchmark`      — cross-domain microbenchmark
"""

from v_universal.benchmark import bench_universal
from v_universal.bio import VBio
from v_universal.consciousness import VConsciousness
from v_universal.core import Version, VLayer, VVersion
from v_universal.economy import VEconomy
from v_universal.hardware import VHardware
from v_universal.law import VLaw
from v_universal.math_layer import VMath
from v_universal.physics import VPhysics
from v_universal.quantum import VQuantum

__all__ = [
    "VLayer",
    "Version",
    "VVersion",
    "VHardware",
    "VQuantum",
    "VBio",
    "VPhysics",
    "VMath",
    "VLaw",
    "VEconomy",
    "VConsciousness",
    "bench_universal",
    "__version__",
]

__version__ = "0.1.0"
