"""V-LAW — constitution as trunk, laws and amendments as versions.

A toy legislative model: the constitution is the trunk; statutes are
committed as versions on top of it; constitutional amendments fork and
commit back into the trunk's ``articles`` dict. Aborting a "bill"
discards it without affecting the legal code.
"""

from __future__ import annotations

from v_universal.core import VLayer, VVersion

_DEFAULT_ARTICLES = {
    "art1": "All persons are equal before the law",
    "art2": "Freedom of speech is guaranteed",
    "art3": "Right to life",
}


class VLaw:
    """A toy constitution + statute book wrapped in a :class:`VLayer`."""

    def __init__(self, articles: dict[str, str] | None = None) -> None:
        self.const = VLayer("LAW:Constitution")
        self.const.set_base("articles", dict(articles or _DEFAULT_ARTICLES))
        self.const.set_base("laws", {})
        self.const.crystallize()

    def propose_law(self, version: VVersion, name: str, text: str) -> None:
        """Stage a new statute into ``version``'s draft."""

        laws = dict(version.read("laws"))
        laws[name] = text
        version.write("laws", laws)

    def amend_constitution(self, version: VVersion, article: str, text: str) -> None:
        """Stage a constitutional amendment into ``version``'s draft."""

        articles = dict(version.read("articles"))
        articles[article] = text
        version.write("articles", articles)

    def has_law(self, name: str) -> bool:
        laws: dict = self.const.get("laws", {})
        return name in laws

    def law_text(self, name: str) -> str:
        laws: dict = self.const.get("laws", {})
        if name not in laws:
            raise KeyError(f"law {name!r} not in the trunk")
        return laws[name]

    def articles(self) -> dict[str, str]:
        return dict(self.const.get("articles"))
