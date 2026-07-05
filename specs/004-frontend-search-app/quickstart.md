# Quickstart: Frontend Search Application

This quickstart describes how Feature 004 should be validated after implementation. It is planning guidance only and does not implement code.

## Prerequisites

- Feature 003 backend can run locally or a compatible deployed API base URL is available.
- Frontend dependencies are installed in the planned `frontend/` application.
- Environment configuration provides the API base URL for `/api/v1` endpoints.

## Environment Configuration

Required frontend configuration:

- API base URL for Feature 003 Backend Search API.

Recommended optional configuration:

- Public site URL for metadata/canonical URLs.
- Indexing toggle for robots behavior by environment.
- Health polling interval if made configurable.

Rules:

- No secrets are required for Feature 004.
- Search state must not be stored in environment configuration or browser storage.

## Manual Verification Flow

1. Start the Feature 003 backend or configure a compatible API base URL.
2. Start the frontend development server from `frontend/`.
3. Open `/` and verify the application shell, top navigation, footer, Market Overview, search toolbar, filters, listing results, pagination, and backend health indicator render.
4. Search using free text and confirm results refresh after debounce.
5. Apply make, model, condition, seller type, price, mileage, and year filters and confirm URL query parameters reflect the state.
6. Change sort and pagination and confirm results refresh automatically.
7. Use Browser Back and Forward to confirm search state restoration.
8. Open a listing detail page at `/listings/[id]` and confirm details load by id.
9. Return from detail and confirm filters, search text, pagination, and scroll position are restored.
10. Switch between light, dark, and system themes and confirm no page reload or state loss.
11. Resize to desktop, laptop, tablet, and mobile widths and confirm no horizontal scrolling.
12. On mobile, open the filter drawer, apply filters, close the drawer, and confirm results update.
13. Simulate backend/API failures with mocks and confirm scoped error states.

## Validation Commands

Run from `frontend/` after implementation:

- Install dependencies.
- Run lint checks.
- Run format checks.
- Run TypeScript checks.
- Run production build.
- Run unit and component tests.
- Run integration tests.
- Run Playwright end-to-end tests.

Exact command names will be defined by the implementation package scripts.

## Expected Test Coverage

- Formatting utilities.
- URL state parsing and serialization.
- API modules and error normalization with mocked endpoints.
- Shared UI components in light and dark themes.
- Home page search/filter/sort/pagination behavior.
- Listing detail page loading, not found, and external marketplace action behavior.
- Browser Back/Forward and scroll restoration.
- Mobile filter drawer behavior.
- Accessibility and keyboard navigation.
- Responsive viewport behavior.

## API Compatibility Check

Only these endpoints may be consumed:

- `GET /api/v1/listings`
- `GET /api/v1/listings/:id`
- `GET /api/v1/listings/filters`
- `GET /api/v1/stats`
- `GET /api/v1/health`

If a desired UI field is missing from the backend response, use safe fallback UI and document the limitation. Do not modify Feature 003 contracts in this feature.
