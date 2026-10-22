"""V-PHYSICS — laws as trunk, world-state as versions.

A two-layer model: a *laws* layer holds immutable physical constants
(gravity, timestep, damping); a *world* layer inherits from laws and
holds the mutable list of bodies. Forking the world lets us run a
multiverse of "what-if" simulations in parallel without committing any
of them back to the trunk.
"""

from __future__ import annotations

from collections.abc import Sequence

from v_universal.core import VLayer, VVersion


class VPhysics:
    """Tiny 2D point-mass simulator wrapped in two :class:`VLayer`s.

    The integration is forward-Euler with a per-step damping coefficient
    — intentionally simple, since the point of the module is the
    versioning abstraction rather than the physics fidelity.
    """

    def __init__(
        self,
        gravity: float = 9.81,
        dt: float = 0.01,
        damping: float = 0.99,
    ) -> None:
        self.laws = VLayer("PHY:Laws")
        self.laws.set_base("G", gravity)
        self.laws.set_base("dt", dt)
        self.laws.set_base("damping", damping)
        self.laws.crystallize()

        self.world = VLayer("PHY:World", base=self.laws)
        self.world.set_base("bodies", [])
        self.world.crystallize()

    def add_body(
        self,
        version: VVersion,
        pos: tuple[float, float],
        vel: tuple[float, float],
        mass: float = 1.0,
    ) -> None:
        """Append a body to ``version``'s world."""

        bodies = list(version.read("bodies"))
        bodies.append(
            {
                "pos": [float(pos[0]), float(pos[1])],
                "vel": [float(vel[0]), float(vel[1])],
                "mass": float(mass),
            }
        )
        version.write("bodies", bodies)

    def step(self, version: VVersion) -> None:
        """Advance the simulation by one ``dt`` step within ``version``."""

        g = version.read("G")
        dt = version.read("dt")
        damping = version.read("damping")
        bodies = [dict(b) for b in version.read("bodies")]
        for b in bodies:
            b["vel"][1] -= g * dt
            b["vel"][0] *= damping
            b["vel"][1] *= damping
            b["pos"][0] += b["vel"][0] * dt
            b["pos"][1] += b["vel"][1] * dt
        version.write("bodies", bodies)

    def run(self, version: VVersion, steps: int) -> None:
        """Convenience: ``step`` ``steps`` times."""

        if steps < 0:
            raise ValueError("steps must be non-negative")
        for _ in range(steps):
            self.step(version)

    @staticmethod
    def position_of(version: VVersion, body_index: int = 0) -> tuple[float, float]:
        bodies: Sequence[dict] = version.read("bodies")
        if not bodies:
            raise IndexError("no bodies in this version")
        if not 0 <= body_index < len(bodies):
            raise IndexError(f"body_index {body_index} out of range [0, {len(bodies)})")
        p = bodies[body_index]["pos"]
        return float(p[0]), float(p[1])
