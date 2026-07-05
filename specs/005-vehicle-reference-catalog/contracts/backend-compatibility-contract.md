# Contract: Backend Compatibility

## Owner

NestJS backend as read-only consumer of PostgreSQL.

## Expectations

- Prisma schema is synchronized after scraper-owned SQL migrations are finalized.
- Existing repositories continue reading listings and catalog data.
- Existing search and filter behavior operates on persisted canonical keys.
- Backend does not canonicalize marketplace values.
- Backend does not contain marketplace-specific alias dictionaries.
- Backend does not reconstruct display names from canonical keys.

## Verification

- Prisma generation succeeds.
- Backend build succeeds.
- Repository and integration compatibility tests pass.
- Code review confirms zero business normalization duplication.

## Compatibility Strategy

Schema changes should be additive or transitional where possible. Any API exposure of display values should consume catalog display data and remain backward compatible unless a future API feature specifies otherwise.
