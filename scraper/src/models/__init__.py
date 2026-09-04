"""Domain models for the ingestion pipeline.

Re-exports every model so callers can import from a single place:
`from src.models import Listing, RunReport, ...`
"""

from src.models.catalog import (
    CatalogSyncReport,
    NormalizationFieldStat,
    NormalizationStatisticsReport,
    VehicleReferenceCatalogRow,
)
from src.models.listing import Listing, RawListing, ValidationResult
from src.models.run import DatasetVersion, IngestionRun, RunReport, RunState, Scope
from src.models.store import (
    BackfillListingCandidate,
    ListingRow,
    MarketplaceSourceRow,
    PersistOutcome,
    RunContext,
    RunRow,
)

__all__ = [
    "BackfillListingCandidate",
    "CatalogSyncReport",
    "DatasetVersion",
    "IngestionRun",
    "Listing",
    "ListingRow",
    "MarketplaceSourceRow",
    "NormalizationFieldStat",
    "NormalizationStatisticsReport",
    "PersistOutcome",
    "RawListing",
    "RunContext",
    "RunReport",
    "RunRow",
    "RunState",
    "Scope",
    "ValidationResult",
    "VehicleReferenceCatalogRow",
]
