"""01 — V-HARDWARE: hardware transactional memory."""

from __future__ import annotations

from v_universal import VHardware


def main() -> None:
    print("=== V-HARDWARE: hardware transactional memory ===")
    hw = VHardware()

    # Begin, write, abort: trunk must be unchanged.
    hw.begin_tx()
    hw.write_reg(0, 42)
    hw.write_reg(1, 100)
    hw.bus_write(0x1000, 0xDEAD)
    print(
        f"in tx:    r0={hw.read_reg(0)}, r1={hw.read_reg(1)}, "
        f"bus.addr=0x{hw.tx['bus'].read('addr'):X}"
    )
    hw.abort_tx()
    print(f"after abort: trunk r0={hw.regs.get('r0')}, bus.addr=0x{hw.bus.get('addr'):X}")

    # Begin, write, commit: trunk must reflect writes.
    hw.begin_tx()
    hw.write_reg(0, 42)
    hw.commit_tx()
    print(f"after commit: trunk r0={hw.regs.get('r0')}")


if __name__ == "__main__":
    main()
