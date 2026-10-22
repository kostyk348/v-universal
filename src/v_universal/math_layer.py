"""V-MATH — axioms as trunk, theorems as versions.

A toy formal-mathematics layer. Each theorem is committed as a version
on top of the axiom trunk. Aborting a "proof" rolls back to the last
committed theorem — the analogue of a failed derivation not polluting
the body of accepted results.
"""

from __future__ import annotations

from v_universal.core import VLayer, VVersion

_DEFAULT_AXIOMS = {
    "refl": "a = a",
    "sym": "a = b -> b = a",
    "trans": "a = b, b = c -> a = c",
    "add": "a + 0 = a",
}


class VMath:
    """An axiomatic system stored as a :class:`VLayer`."""

    def __init__(self, axioms: dict[str, str] | None = None) -> None:
        self.axioms = VLayer("MATH:Axioms")
        self.axioms.set_base("axioms", dict(axioms or _DEFAULT_AXIOMS))
        self.axioms.set_base("theorems", {})
        self.axioms.crystallize()

    def prove(self, version: VVersion, theorem: str, steps: list[str]) -> None:
        """Stage a theorem + its proof into ``version``'s draft.

        The proof is a list of human-readable strings; each typically
        references an axiom or a previously committed theorem.
        """

        theorems = dict(version.read("theorems"))
        theorems[theorem] = steps
        version.write("theorems", theorems)

    def has_theorem(self, name: str) -> bool:
        theorems: dict = self.axioms.get("theorems", {})
        return name in theorems

    def proof_of(self, name: str) -> list[str]:
        theorems: dict = self.axioms.get("theorems", {})
        if name not in theorems:
            raise KeyError(f"theorem {name!r} not in the trunk")
        return list(theorems[name])
