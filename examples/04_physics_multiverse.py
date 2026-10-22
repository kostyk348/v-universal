"""04 — V-PHYSICS: laws as trunk, world-states as versions (multiverse)."""

from __future__ import annotations

from v_universal import VPhysics


def main() -> None:
    print("=== V-PHYSICS: laws as trunk, states as versions ===")
    phy = VPhysics()

    # Run one body for 100 steps under Earth gravity.
    v = phy.world.fork()
    phy.add_body(v, pos=(0.0, 10.0), vel=(1.0, 0.0))
    phy.run(v, 100)
    x, y = VPhysics.position_of(v)
    print(f"after 100 steps (Earth):   pos=({x:.2f}, {y:.2f})")

    # Multiverse: run the same body under different gravities (Moon / Earth / Jupiter).
    print("multiverse: different G values")
    for g, name in [(1.62, "Moon"), (9.81, "Earth"), (24.79, "Jupiter")]:
        branch = phy.world.fork()
        branch.write("G", g)  # local override of a law in this branch only
        phy.add_body(branch, pos=(0.0, 10.0), vel=(1.0, 0.0))
        phy.run(branch, 100)
        bx, by = VPhysics.position_of(branch)
        print(f"  {name:8s} G={g:5.2f}: pos=({bx:.2f}, {by:.2f})")
        branch.abort()  # none of these get committed

    # Trunk laws must still be Earth gravity.
    print(f"trunk G after multiverse: {phy.laws.get('G')}")


if __name__ == "__main__":
    main()
