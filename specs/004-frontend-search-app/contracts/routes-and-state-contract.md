# Contract: Routes And Search State

## Routes

### `/`

Purpose: Search homepage.

Composes:

- Market Overview
- SearchToolbar
- FilterSidebar or mobile Filter Drawer
- ResultsGrid
- ListingCard
- Pagination
- Backend availability indicator in the shell navigation

### `/listings/[id]`

Purpose: Listing detail page.

Composes:

- Image Gallery
- Vehicle Summary
- Vehicle Specifications
- Marketplace Action

Route parameter:

- `id: string`

Rules:

- Detail pages load by listing id only.
- Detail pages must not require search state to exist.

## Search URL Parameters

Supported query parameters on `/`:

- `q`
- `make`
- `model`
- `condition`
- `sellerType`
- `priceMin`
- `priceMax`
- `kmMin`
- `kmMax`
- `yearFrom`
- `yearTo`
- `sort`
- `page`
- `limit`

Rules:

- URL query parameters are the complete source of truth for search state.
- Invalid or unsupported values are normalized or removed.
- Filter and sort changes reset `page` to 1.
- Pagination changes update `page` and preserve other criteria.
- Clear Filters returns to default search state.

## Browser Navigation

- Browser Back restores the previous search URL state.
- Browser Forward restores the next search URL state.
- Returning from detail restores previous filters, search text, pagination, and scroll position.
- Pagination changes scroll to the top of the results area or page content.

## Search Interaction

- Text search uses debounce before updating URL/API state.
- Filter changes refresh automatically.
- Sort changes refresh automatically.
- Pagination changes refresh automatically.
- No explicit Search button is required after initial page load.
