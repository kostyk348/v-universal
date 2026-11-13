<div align="center">

<img src="docs/banner.svg" alt="v-universal banner" width="1000">

# V-UNIVERSAL

[![CI](https://img.shields.io/badge/CI-pytest%20%2B%20ruff-blue)](.github/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![Built with uv](https://img.shields.io/badge/built%20with-uv-purple)](https://docs.astral.sh/uv/)

</div>

---


> One versioning model — `trunk + version tree` — applied to **nine**
> different domains. Hardware, quantum, biology, physics, math, law,
> economy and consciousness, all modelled with the same three
> primitives: `fork / write / commit`.

[![CI](https://img.shields.io/badge/CI-pytest%20%2B%20ruff-blue)](.github/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![Built with uv](https://img.shields.io/badge/built%20with-uv-purple)](https://docs.astral.sh/uv/)

Documentation in other languages: [**Русский**](README.ru.md)

---

## TL;DR

Every domain in this library is built on the same three primitives:

```python
v = layer.fork()      # cheap in-memory branch
v.write(key, value)   # stage a change into the draft
v.commit()            # publish the draft back to the trunk
# or
v.abort()             # throw the draft away
```

That is literally all `git` does. The interesting claim of V-UNIVERSAL is
that **the same three primitives suffice to model a surprisingly wide
range of systems** — from hardware transactional memory, through quantum
state vectors and biological genomes, all the way to a toy model of
consciousness. The library is a worked example of that claim, with
tests.

## The nine domains

| Module | Trunk | Version | Commit |
|---|---|---|---|
| `VHardware` | registers / bus / cache | transaction | atomic publish |
| `VQuantum` | state vector | gate application | measurement (collapse) |
| `VBio` | genome | mutation | selection |
| `VPhysics` | laws + world | branch of initial conditions | committed history line |
| `VMath` | axioms | theorem + proof | accepted theorem |
| `VLaw` | constitution | bill | enacted statute |
| `VEconomy` | account ledger | pending transfer | settled transaction |
| `VConsciousness` | sensations + emotions | thought + decision | acted-on decision |
| `bench_universal` | — | cross-domain microbenchmark | — |

## Installation

```bash
git clone https://github.com/your-org/v-universal.git
cd v-universal
uv sync --extra dev         # or: pip install -e ".[dev]"
pytest                      # <1 second on CPU
```

## Quick start

```python
from v_universal import VHardware

hw = VHardware()
hw.begin_tx()           # fork all three layers
hw.write_reg(0, 42)
hw.bus_write(0x1000, 0xDEAD)
hw.abort_tx()           # discard — trunk is unchanged

hw.begin_tx()
hw.write_reg(0, 42)
hw.commit_tx()          # publish — trunk now has r0=42
```

The same pattern works for every other domain:

```python
from v_universal import VEconomy, InsufficientFunds

eco = VEconomy()
v = eco.ledger.fork()
try:
    eco.transfer(v, "alice", "bob", 100)
    v.commit()
except InsufficientFunds:
    v.abort()
```

## Examples

| File | Domain | What it shows |
|---|---|---|
| `01_hardware.py` | V-HARDWARE | HTM: begin / write / abort / commit |
| `02_quantum.py` | V-QUANTUM | Hadamard superposition, measurement collapse |
| `03_bio.py` | V-BIO | Mutate 10 candidates, select + commit the best |
| `04_physics_multiverse.py` | V-PHYSICS | Same body under Moon / Earth / Jupiter gravity |
| `05_math.py` | V-MATH | Axioms → theorems, with a failed proof that is aborted |
| `06_law.py` | V-LAW | Statutes + constitutional amendments + a bill that fails |
| `07_economy.py` | V-ECONOMY | Transfers, insufficient funds, parallel branches |
| `08_consciousness.py` | V-CONSCIOUSNESS | Thoughts, decisions, regret |
| `09_benchmark.py` | — | Cross-domain microbenchmark |

Run any of them with `python examples/<file>.py`.

## How it works

### Core primitives

The whole library is three classes in `v_universal/core.py`:

* **`Version`** — an immutable node in a version tree. Holds a `changes`
  dict relative to its parent. Reading a key walks up the parent chain.
* **`VLayer`** — the trunk. Owns a root `Version`, the current head, a
  flat last-writer-wins index, and an optional base layer for
  inheritance. `crystallize()` freezes `set_base` so initial values
  must be defined up-front.
* **`VVersion`** — a cheap in-memory fork. Writes go into a `draft`
  dict; `commit()` publishes the draft to the trunk, `abort()` discards
  it.

That's it. Every domain module adds domain-specific accessors on top —
`VHardware.write_reg`, `VQuantum.apply_gate`, `VBio.mutate`, etc. — but
the underlying mechanics are always `fork / write / commit`.

### Why bother?

Three reasons:

1. **Pedagogy.** Once you internalise `fork / write / commit`, you
   start seeing it everywhere — in `git`, in database transactions, in
   blockchain consensus, in hardware TM, in evolutionary dynamics.
   V-UNIVERSAL makes the pattern concrete across nine domains with the
   same three Python classes.

2. **Composition.** Because every domain uses the same primitives, you
   can build hybrid systems. A genetic algorithm whose fitness function
   runs a physics simulation. A legal system that settles financial
   transfers atomically. The primitives compose for free.

3. **Testability.** Every domain's behaviour reduces to "did the
   commit happen, did the abort happen". The 85-test suite is short
   precisely because the abstraction collapses nine test surfaces into
   one.

### Limitations

This is a research preview, not a production library:

* **Persistence**: nothing is serialised. `VLayer` lives in RAM; if the
  process dies, the trunk is gone.
* **Concurrency**: no locking. Two threads committing to the same
  layer will race.
* **Performance**: `Version.resolve` walks the parent chain on every
  read. Fine for thousands of versions, bad for millions. A flat
  snapshot per version would fix this.
* **Quantum**: only single-qubit + CNOT gates, no GPU acceleration,
  state vector formalism only (no tensor networks).

## Repository layout

```
v-universal/
├── src/v_universal/
│   ├── core.py              # Version, VLayer, VVersion
│   ├── hardware.py          # VHardware
│   ├── quantum.py           # VQuantum + gate helpers
│   ├── bio.py               # VBio
│   ├── physics.py           # VPhysics (multiverse)
│   ├── math_layer.py        # VMath (axioms + theorems)
│   ├── law.py               # VLaw (constitution + statutes)
│   ├── economy.py           # VEconomy (ledger + transfers)
│   ├── consciousness.py     # VConsciousness (sensations + thoughts)
│   └── benchmark.py         # bench_universal
├── tests/                   # 10 pytest modules, 85 tests total
├── examples/                # 9 runnable demos
├── notebooks/               # Cleaned .ipynb
├── .github/workflows/ci.yml # Python 3.10 / 3.11 / 3.12
├── pyproject.toml           # uv + hatchling + ruff
└── README.md / README.ru.md
```

## Status

Research preview. Apache-2.0. Contributions welcome — see
[CONTRIBUTING](#contributing).

## Contributing

1. `uv sync --extra dev`
2. `pre-commit install`
3. Add a test under `tests/` that fails without your change.
4. `pytest` and `ruff check .` must be green.
5. Open a PR — CI runs on Python 3.10/3.11/3.12.

## Citation

```bibtex
@misc{vuniversal2025,
  title  = {V-UNIVERSAL: one versioning model for everything},
  author = {V-UNIVERSAL Contributors},
  year   = {2025},
  note   = {Research preview, Apache-2.0}
}
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
