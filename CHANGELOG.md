# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2025-01-15

### Added
- Initial extraction from the `V-NET.ipynb` proof-of-concept.
- Core versioning primitives: `Version`, `VLayer`, `VVersion`.
- Eight domain modules built on the core:
  - `VHardware` — hardware transactional memory
  - `VQuantum` — state-vector quantum simulator with H/X/Z gates + CNOT
  - `VBio` — genome + mutation + selection
  - `VPhysics` — laws + world + multiverse
  - `VMath` — axioms + theorems
  - `VLaw` — constitution + statutes + amendments
  - `VEconomy` — ledger + transfers with insufficient-funds rollback
  - `VConsciousness` — sensations + emotions + thoughts + decisions
- Cross-domain microbenchmark `bench_universal`.
- 9 example scripts under `examples/`.
- 10 test modules under `tests/` (85 tests total).
- GitHub Actions CI matrix on Python 3.10 / 3.11 / 3.12.
- Bilingual README (English + Russian).
- Apache 2.0 license.

[0.1.0]: https://github.com/your-org/v-universal/releases/tag/v0.1.0
