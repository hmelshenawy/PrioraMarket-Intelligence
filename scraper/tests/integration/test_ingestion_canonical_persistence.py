from __future__ import annotations

from datetime import datetime, timezone

from src.config import Config
from src.fetch.algolia import PageMetadata
from src.models import RawListing, Scope
from src.pipeline import IngestionPipeline
from tests.fakes import InMemoryStorageAdapter


class _Adapter:
    def fetch(self, scope):
        raw_payload = {"id": "native-1", "make": "Mercedes-Benz"}
        yield [
            RawListing(
                marketplace="dubizzle",
                marketplace_listing_id="native-1",
                uuid="uuid-1",
                raw_payload=raw_payload,
                extracted_fields={
                    "uuid": "uuid-1",
                    "make": "Mercedes-Benz",
                    "model": "C-Class",
                    "price_aed": 100000,
                    "year": 2022,
                    "km": 10000,
                    "fuel": "Gasoline",
                    "transmission": "Auto",
                    "specs": "GCC Specs",
                    "body_type": "Sedan",
                    "color": "Polar White",
                },
                fetched_at=datetime.now(timezone.utc),
                scrape_run_id="run-us1",
                condition=scope.condition,
                make_slug="mercedes-benz",
            )
        ], PageMetadata(page=0, hits_on_page=1, nb_pages=1, nb_hits=1)


def _config(tmp_path):
    return Config(
        algolia_app_id="x",
        algolia_api_key="x",
        algolia_index="idx",
        algolia_url="https://example.test",
        hits_per_page=20,
        max_pages=1,
        output_dir=tmp_path,
        retry_attempts=1,
        retry_backoff=0,
        rate_limit_min_seconds=0,
        rate_limit_max_seconds=0,
        request_timeout_seconds=1,
        normalization_version="norm-1",
        enable_canonicalization=True,
        enable_structured_logging=False,
        enable_csv_storage=True,
    )


def test_ingestion_preserves_raw_and_persists_canonical_values(tmp_path) -> None:
    storage = InMemoryStorageAdapter()
    pipeline = IngestionPipeline(_config(tmp_path), _Adapter(), storage)

    result = pipeline.run(Scope("dubizzle", "used", "mercedes-benz"), "run-us1")

    assert len(result.accepted) == 1
    listing = result.accepted[0]
    assert listing.make == "mercedesbenz"
    assert listing.model == "cclass"
    assert listing.fuel_type == "petrol"
    assert listing.transmission == "automatic"
    assert listing.regional_spec == "gcc"
    assert listing.color == "polarwhite"
    assert listing.canonicalization_version == "canonical-key-1"
    assert storage.raw[0].raw_payload == {"id": "native-1", "make": "Mercedes-Benz"}
    assert storage.normalization_statistics
