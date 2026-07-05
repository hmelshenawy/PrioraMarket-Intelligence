# Contract: UI Foundation

## Application Shell

Required shell slots:

- Top navigation
- Main content area
- Footer
- Responsive container
- Global providers
- Global error boundary

Rules:

- All current and future pages reuse the shell.
- Shell must not contain feature-specific business logic.

## Navigation

Required items:

- PrioraMarket logo
- Search/Home navigation
- Theme switcher
- Backend availability indicator
- Reserved space for future navigation items

Rules:

- Navigation is reusable by future frontend features.
- Navigation must remain keyboard and screen-reader accessible.

## Theme Contract

Modes:

- Light
- Dark
- System

Rules:

- ThemeProvider owns theme mode and resolved theme.
- Theme selection persists across visits.
- System mode follows system color-scheme changes.
- Theme changes do not reload the page or lose current route/search state.
- All shared UI components support light and dark themes.

## Shared UI Components

Required components:

- Button
- IconButton
- Input
- SearchInput
- Select
- RangeInput
- Card
- Badge
- Tag
- Pagination
- Spinner
- Skeleton
- EmptyState
- ErrorState
- Alert
- Modal
- Drawer
- Tooltip
- StatusIndicator
- Divider

Rules:

- Shared UI components use design tokens.
- Shared UI components do not depend on feature-specific logic.
- Shared UI components expose accessible names, roles, focus behavior, and disabled/loading states where applicable.

## Design Tokens

Token categories:

- Colors
- Typography
- Spacing
- Border radius
- Shadows
- Z-index
- Transitions
- Breakpoints

Rules:

- Components use semantic token roles rather than hard-coded values.
- Tokens support light and dark themes.

## Loading And Error UI

Required loading states:

- Page Skeleton
- Card Skeleton
- Detail Skeleton
- Summary Skeleton
- Filter Skeleton

Required error states:

- Network Error
- Backend Offline
- Empty Search Results
- Listing Not Found
- Unexpected Error

Rules:

- Loading and error states are scoped to the affected section whenever possible.
- Empty search results include friendly illustration or placeholder, explanation, Clear Filters action, and immediate search continuation.
