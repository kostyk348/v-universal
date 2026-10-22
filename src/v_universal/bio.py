"""V-BIO — genome as trunk, mutations as versions.

The genome is the trunk. Each mutation creates a fork; selection
commits the best fork back into the trunk (the next generation). The
abstraction mirrors exactly what bioinformaticians do when they
reason about "what if this base were different".
"""

from __future__ import annotations

import random
from collections.abc import Callable

from v_universal.core import VLayer, VVersion

_DEFAULT_ALPHABET = "ACGT"


class VBio:
    """A simple genetic-algebra wrapper around a :class:`VLayer`.

    The fitness function is pluggable: by default it counts GC-content
    (a stand-in for any real biological objective). Pass a custom
    callable to :meth:`evaluate` to plug in your own.
    """

    def __init__(
        self,
        genome_size: int = 64,
        seed: int | None = 42,
        alphabet: str = _DEFAULT_ALPHABET,
    ) -> None:
        if genome_size <= 0:
            raise ValueError("genome_size must be positive")
        rng = random.Random(seed)
        self.alphabet = alphabet
        self.genome_size = genome_size
        self.genome = VLayer("BIO:Genome")
        self.genome.set_base(
            "seq",
            [rng.choice(alphabet) for _ in range(genome_size)],
        )
        self.genome.set_base("fitness", 0.0)
        self.genome.crystallize()
        self._rng = rng

    def mutate(self, version: VVersion, rate: float = 0.1) -> int:
        """In-place point mutation of ``version``'s sequence.

        Returns the number of bases that were actually changed.
        """

        if not 0.0 <= rate <= 1.0:
            raise ValueError("rate must lie in [0, 1]")
        seq = list(version.read("seq"))
        changes = 0
        for i in range(len(seq)):
            if self._rng.random() < rate:
                seq[i] = self._rng.choice(self.alphabet)
                changes += 1
        version.write("seq", seq)
        return changes

    def evaluate(
        self,
        version: VVersion,
        fitness: Callable[[list[str]], float] | None = None,
    ) -> float:
        """Compute and store the fitness of ``version``'s sequence.

        Defaults to GC-content. Pass a custom ``fitness`` callable that
        accepts a list of characters and returns a float.
        """

        seq = version.read("seq")
        fn = fitness or _gc_content
        score = float(fn(seq))
        version.write("fitness", score)
        return score

    def select(
        self,
        population: list[VVersion],
        k: int = 1,
    ) -> list[VVersion]:
        """Return the ``k`` fittest versions from ``population``.

        Reads the ``fitness`` field from each version's draft (so the
        caller must have called :meth:`evaluate` first).
        """

        if not population:
            raise ValueError("population must be non-empty")
        if not 1 <= k <= len(population):
            raise ValueError(f"k must lie in [1, {len(population)}]")
        scored = sorted(
            population,
            key=lambda v: v.read("fitness", 0.0),
            reverse=True,
        )
        return scored[:k]


def _gc_content(seq: list[str]) -> float:
    """Default fitness: fraction of G/C bases in ``seq``."""

    if not seq:
        return 0.0
    gc = sum(1 for c in seq if c in "GC")
    return gc / len(seq)
