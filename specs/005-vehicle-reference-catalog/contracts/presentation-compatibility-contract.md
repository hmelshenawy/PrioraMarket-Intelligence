# Contract: Presentation Compatibility

## Owner

Presentation consumers, including the Next.js frontend.

## Expectations

- Presentation consumers use display values supplied from Vehicle Reference Catalog-backed data.
- Presentation consumers do not reconstruct names from canonical keys.
- Canonical values such as `mercedesbenz` and `cclass` are operational identifiers, not display labels.
- Display values such as `Mercedes-Benz` and `C-Class` originate from catalog data.

## Out Of Scope

- Frontend implementation details.
- Client-side canonicalization.
- Client-side marketplace-specific mappings.
- New caching requirements.

## Future Opportunity

Display mapping can be cached later by backend or presentation consumers if needed, provided catalog display values remain authoritative and canonical keys remain immutable.
