"""Read-only workspace skill catalogue dashboard."""

from .catalog import discover_catalog
from .models import CatalogInventory, CatalogSkill

__all__ = ["CatalogInventory", "CatalogSkill", "discover_catalog"]
