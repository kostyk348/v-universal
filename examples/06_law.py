"""06 — V-LAW: constitution as trunk, laws as versions."""

from __future__ import annotations

from v_universal import VLaw


def main() -> None:
    print("=== V-LAW: constitution as trunk, laws as versions ===")
    law = VLaw()
    print(f"constitution articles: {list(law.articles().keys())}")

    v1 = law.const.fork()
    law.propose_law(v1, "law_1", "Flat tax 13%")
    v1.commit()
    print(f"after law_1: committed laws = {list(law.const.get('laws').keys())}")

    v2 = law.const.fork()
    law.propose_law(v2, "law_2", "Retirement age 65")
    v2.commit()
    print(f"after law_2: committed laws = {list(law.const.get('laws').keys())}")

    # Constitutional amendment.
    v3 = law.const.fork()
    law.amend_constitution(v3, "art4", "Right to education")
    v3.commit()
    print(f"constitution after amendment: {list(law.articles().keys())}")

    # An unpopular bill that does NOT pass (abort).
    v4 = law.const.fork()
    law.propose_law(v4, "law_3", "Ban everything")
    print(f"branch laws: {list(v4.read('laws').keys())}")
    v4.abort()
    print(f"after abort: laws = {list(law.const.get('laws').keys())}")


if __name__ == "__main__":
    main()
