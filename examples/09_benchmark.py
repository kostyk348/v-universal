"""09 — Cross-domain benchmark."""

from __future__ import annotations

from v_universal import bench_universal
from v_universal.benchmark import format_results


def main() -> None:
    n = 10000
    print(f"=== BENCHMARK: {n} fork/abort cycles per domain ===")
    results = bench_universal(n=n)
    print(format_results(results, n=n))


if __name__ == "__main__":
    main()
