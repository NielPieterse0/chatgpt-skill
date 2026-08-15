"""Repository bootstrap for the src-layout skill catalogue dashboard package."""

from pathlib import Path

_SOURCE_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "skill_catalog_dashboard"
if str(_SOURCE_PACKAGE) not in __path__:
    __path__.append(str(_SOURCE_PACKAGE))
