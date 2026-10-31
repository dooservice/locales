"""Every language says what English says: same files, same keys, same blanks.

English is the reference. A language may lack a key, and then reads English for it, but it
may not have a key English does not have, nor drop or invent a blank (`{name}` or
`{{name}}`), because the code fills the blanks English names. A file a language lacks reads
in English whole. `--strict` fails on anything read in English: every language complete.

    python3 tools/check.py
    python3 tools/check.py --strict
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = "en"
PLURALS = ("_zero", "_one", "_two", "_few", "_many", "_other")


class Blanks:
    """The names between braces of a text: `{name}` and `{{name}}` read the same."""

    def __init__(self, text: str) -> None:
        self.names: set[str] = set()
        rest = text
        while "{" in rest:
            _, _, after = rest.partition("{")
            name, closed, rest = after.lstrip("{").partition("}")
            if closed:
                self.names.add(name.strip().split(",")[0].strip())


class Catalog:
    """One JSON file's texts, by their dotted key."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.texts: dict[str, str] = {}
        self.read(json.loads(path.read_text(encoding="utf-8")), "")

    def read(self, value: object, prefix: str) -> None:
        if isinstance(value, dict):
            for name, inner in value.items():
                self.read(inner, f"{prefix}{name}.")
        elif isinstance(value, str):
            self.texts[prefix.removesuffix(".")] = value
        elif isinstance(value, list):
            for index, inner in enumerate(value):
                self.read(inner, f"{prefix}{index}.")


class Check:
    def __init__(self, strict: bool) -> None:
        self.strict = strict
        self.problems: list[str] = []
        self.missing = 0

    def run(self) -> int:
        languages = [entry["code"] for entry in json.loads((ROOT / "languages.json").read_text(encoding="utf-8"))]
        if REFERENCE not in languages:
            self.problems.append(f"languages.json must list {REFERENCE}")
        files = sorted(path.relative_to(ROOT / REFERENCE) for path in (ROOT / REFERENCE).rglob("*.json"))
        for language in languages:
            if language != REFERENCE:
                self.language(language, files)
        for folder in sorted(path.name for path in ROOT.iterdir() if path.is_dir() and len(path.name) == 2):
            if folder not in languages:
                self.problems.append(f"{folder}/ is not in languages.json")
        for problem in self.problems:
            print(problem)
        print(f"{len(languages)} languages, {len(files)} files, {self.missing} texts read in English")
        return 1 if self.problems else 0

    def language(self, language: str, files: list[Path]) -> None:
        for relative in files:
            path = ROOT / language / relative
            if not path.is_file():
                self.missing += len(Catalog(ROOT / REFERENCE / relative).texts)
                if self.strict:
                    self.problems.append(f"{language}/{relative} is missing")
                continue
            self.compare(Catalog(ROOT / REFERENCE / relative), Catalog(path), f"{language}/{relative}")

    def compare(self, reference: Catalog, own: Catalog, where: str) -> None:
        for key in own.texts.keys() - reference.texts.keys():
            if not self.plural_of(key, reference):
                self.problems.append(f"{where}: {key} is not in English")
        for key, text in reference.texts.items():
            if key not in own.texts:
                self.missing += 1
                if self.strict:
                    self.problems.append(f"{where}: {key} is missing")
                continue
            expected, found = Blanks(text).names, Blanks(own.texts[key]).names
            if expected != found:
                self.problems.append(f"{where}: {key} has blanks {sorted(found)}, English has {sorted(expected)}")

    @staticmethod
    def plural_of(key: str, reference: Catalog) -> bool:
        """A plural form another language needs and English does not, such as `_many`."""
        for suffix in PLURALS:
            if key.endswith(suffix) and f"{key.removesuffix(suffix)}_other" in reference.texts:
                return True
        return False


if __name__ == "__main__":
    sys.exit(Check("--strict" in sys.argv).run())
