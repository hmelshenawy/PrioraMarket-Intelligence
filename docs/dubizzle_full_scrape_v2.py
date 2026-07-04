#!/usr/bin/env python3
"""
Dubizzle Full Scrape v2 — Used + New Cars
- Scrapes each make separately to bypass Algolia 10k limit
- Generates two separate CSVs: Used Cars + New Cars
- Merges with previous CSVs (dedup by uuid, newest data wins)
"""

import csv
import random
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present

ALGOLIA_APP_ID = "WD0PTZ13ZS"
ALGOLIA_API_KEY = "cef139620248f1bc328a00fddc7107a6"
ALGOLIA_INDEX = "by_added_desc_motors.com"
ALGOLIA_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/*/queries"
HITS_PER_PAGE = 20
OUTPUT_DIR = Path("/home/openclaw/.openclaw/workspace/data/dubizzle")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Previous sheets to merge with
OLD_USED_CSV = OUTPUT_DIR / "Dubai_Used_Cars_25363_listings.csv"
OLD_NEW_CSV = OUTPUT_DIR / "Dubai_New_Cars_4142_listings.csv"

MAKE_SLUGS = [
    "mercedes-benz",
    "toyota",
    "bmw",
    "nissan",
    "land-rover",
    "ford",
    "porsche",
    "audi",
    "jeep",
    "volkswagen",
    "hyundai",
    "kia",
    "mitsubishi",
    "ferrari",
    "lexus",
    "chevrolet",
    "rolls-royce",
    "lamborghini",
    "mg",
    "dodge",
    "byd",
    "mazda",
    "honda",
    "infiniti",
    "jetour",
    "bentley",
    "tesla",
    "cadillac",
    "mini",
    "suzuki",
    "gmc",
    "peugeot",
    "jaguar",
    "lincoln",
    "maserati",
    "renault",
    "gac",
    "volvo",
    "aston-martin",
    "mercedes-maybach",
    "geely",
    "alfa-romeo",
    "jac",
    "ram",
    "genesis",
    "rox",
    "zeekr",
    "changan",
    "mclaren",
    "chery",
    "isuzu",
    "xiaomi",
]


def build_filter(make_slug: str, condition: str) -> str:
    return f'("category_v2.slug_paths":"motors/{condition}-cars/{make_slug}") AND ("site.id":2)'


def extract(hit: dict) -> dict:
    raw_details = hit.get("details") or {}

    def dval(key):
        entry = raw_details.get(key, {})
        if isinstance(entry, dict):
            return (entry.get("en") or {}).get("value")
        return None

    places = hit.get("places") or {}
    place_en = places.get("en", []) if isinstance(places, dict) else []
    location_str = ", ".join(place_en) if place_en else None

    cats = (hit.get("category_v2") or {}).get("slug_paths", [])
    make_slug = next((c.split("/")[2] for c in cats if c.count("/") == 2), None)
    model_slug = next((c.split("/")[3] for c in cats if c.count("/") == 3), None)

    name = hit.get("name") or {}
    name_en = name.get("en") if isinstance(name, dict) else name
    nbhd = hit.get("neighbourhood") or {}
    nbhd_en = nbhd.get("en") if isinstance(nbhd, dict) else nbhd

    return {
        "id": hit.get("id"),
        "uuid": hit.get("uuid"),
        "name": name_en,
        "price_aed": hit.get("price"),
        "year": hit.get("year"),
        "km": hit.get("kilometers"),
        "make": make_slug.replace("-", " ").title() if make_slug else None,
        "model": model_slug.replace("-", " ").title() if model_slug else None,
        "trim": (hit.get("motors_trim") or {}).get("name"),
        "body_type": dval("Body Type"),
        "fuel": dval("Fuel Type"),
        "transmission": dval("Transmission Type"),
        "color": dval("Exterior Color"),
        "specs": dval("Regional Specs"),
        "seller_type": hit.get("seller_type"),
        "seller": (hit.get("user") or {}).get("name"),
        "is_verified": hit.get("is_verified_user"),
        "is_agent": hit.get("seller_account_type") == "AG",
        "neighbourhood": nbhd_en,
        "location": location_str,
        "added": hit.get("added"),
        "url": f"https://dubai.dubizzle.com{hit.get('uri', '')}",
        "photos_count": hit.get("photos_count", 0),
    }


def scrape_make(session, make: str, condition: str) -> list:
    filters = build_filter(make, condition)
    listings = []
    page = 0
    total_pages = 1

    while page < total_pages:
        params = "&".join(
            [
                f"hitsPerPage={HITS_PER_PAGE}",
                f"page={page}",
                f"filters={filters}",
                "attributesToRetrieve=id,uuid,name,price,year,kilometers,details,category_v2,seller_type,user,is_verified_user,seller_account_type,neighbourhood,places,uri,added,photos_count,motors_trim",
            ]
        )
        try:
            r = session.post(
                ALGOLIA_URL,
                json={"requests": [{"indexName": ALGOLIA_INDEX, "params": params}]},
                timeout=15,
            )
            r.raise_for_status()
            result = r.json()["results"][0]
            if page == 0:
                total_pages = min(result.get("nbPages", 1), 500)
                total_hits = result.get("nbHits", 0)
                if total_hits == 0:
                    break
            listings.extend([extract(h) for h in result.get("hits", [])])
            page += 1
            time.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            print(f"    ✗ Error page {page}: {e}")
            break

    return listings


def load_old_csv(path: Path) -> dict:
    """Load old CSV into dict keyed by uuid (or id fallback)."""
    if not path.exists():
        print(f"   ⚠ No previous CSV found at {path.name} — starting fresh")
        return {}
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row.get("uuid") or row.get("id")
            if key:
                rows[key] = row
    print(f"   📂 Loaded {len(rows):,} old listings from {path.name}")
    return rows


def save_csv(listings: list, path: Path):
    if not listings:
        print(f"   ⚠ No listings to save to {path.name}")
        return
    keys = list(listings[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(listings)
    print(f"   💾 Saved {len(listings):,} listings → {path.name}")


def print_summary(label: str, listings: list):
    prices = sorted([float(l["price_aed"]) for l in listings if l.get("price_aed")])
    print(f"\n📊 {label} — Price Summary (AED):")
    if prices:
        print(f"   Count:  {len(prices):,}")
        print(f"   Min:    {prices[0]:>12,.0f}")
        print(f"   Max:    {prices[-1]:>12,.0f}")
        print(f"   Median: {prices[len(prices)//2]:>12,.0f}")
        print(f"   Avg:    {sum(prices)/len(prices):>12,.0f}")
    makes = Counter(l["make"] for l in listings if l.get("make"))
    print("\n🏷  Top Makes:")
    for make, count in makes.most_common(10):
        print(f"   {make:<25} {count:>6,}")


def scrape_condition(session, condition: str, label: str, old_csv: Path) -> dict:
    print(f"\n{'='*60}")
    print(f"🚗 Scraping {label} — {len(MAKE_SLUGS)} makes")
    print(f"{'='*60}")

    # Load old data first (will be overwritten by new on conflict)
    old_data = load_old_csv(old_csv)

    new_listings = {}
    for i, make in enumerate(MAKE_SLUGS, 1):
        print(f"  [{i:>2}/{len(MAKE_SLUGS)}] {make:<25}", end=" ", flush=True)
        listings = scrape_make(session, make, condition)
        new = 0
        for l in listings:
            key = l.get("uuid") or l.get("id")
            if key:
                new_listings[key] = l  # new data wins
                new += 1
        print(f"✓ {len(listings):>5} listings ({new} unique) | Running: {len(new_listings):,}")

    # Merge: start with old, overwrite with new
    merged = {**old_data}
    added_new = 0
    updated = 0
    for key, listing in new_listings.items():
        if key in merged:
            updated += 1
        else:
            added_new += 1
        merged[key] = listing

    final = list(merged.values())
    print(f"\n   ✅ {label} merge complete:")
    print(f"      Old listings:     {len(old_data):,}")
    print(f"      New from scrape:  {len(new_listings):,}")
    print(f"      Brand new (added):{added_new:,}")
    print(f"      Updated:          {updated:,}")
    print(f"      Total merged:     {len(final):,}")

    return final


def main():
    session = requests.Session()
    session.headers.update(
        {
            "X-Algolia-Application-Id": ALGOLIA_APP_ID,
            "X-Algolia-API-Key": ALGOLIA_API_KEY,
            "Content-Type": "application/json",
        }
    )

    ts_start = datetime.now()
    ts = ts_start.strftime("%Y%m%d_%H%M%S")
    print(f"🏁 Dubizzle Full Scrape v2 — Started: {ts_start.strftime('%Y-%m-%d %H:%M:%S')}")

    # ── USED CARS ──────────────────────────────────────────
    used_listings = scrape_condition(session, "used", "Used Cars", OLD_USED_CSV)
    used_out = OUTPUT_DIR / f"Dubai_Used_Cars_{len(used_listings)}_listings_{ts}.csv"
    save_csv(used_listings, used_out)
    print_summary("Used Cars", used_listings)

    # ── NEW CARS ───────────────────────────────────────────
    new_listings = scrape_condition(session, "new", "New Cars", OLD_NEW_CSV)
    new_out = OUTPUT_DIR / f"Dubai_New_Cars_{len(new_listings)}_listings_{ts}.csv"
    save_csv(new_listings, new_out)
    print_summary("New Cars", new_listings)

    # ── FINAL SUMMARY ──────────────────────────────────────
    elapsed = (datetime.now() - ts_start).seconds // 60
    print(f"\n{'='*60}")
    print(f"🎉 ALL DONE in {elapsed} min")
    print(f"   Used Cars → {used_out.name}")
    print(f"   New Cars  → {new_out.name}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
