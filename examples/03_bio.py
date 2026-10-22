"""03 — V-BIO: genome as trunk, mutations as versions."""

from __future__ import annotations

from v_universal import VBio


def main() -> None:
    print("=== V-BIO: genome as trunk, mutations as versions ===")
    bio = VBio(genome_size=64, seed=42)
    print(f"base genome: {''.join(bio.genome.get('seq')[:16])}...")

    # Generate 10 mutated candidates and pick the best by fitness.
    population = []
    for _ in range(10):
        v = bio.genome.fork()
        bio.mutate(v, rate=0.1)
        bio.evaluate(v)
        population.append(v)

    best = bio.select(population, k=1)[0]
    print(f"best fitness:  {best.read('fitness'):.3f}")
    print(f"worst fitness: {population[-1].read('fitness'):.3f}")

    # Commit the winner.
    best.commit()
    print(f"committed genome: {''.join(bio.genome.get('seq')[:16])}...")
    for v in population:
        if v is not best:
            v.abort()
    print("aborted the rest")


if __name__ == "__main__":
    main()
