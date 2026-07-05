import {
  displayOrCanonical,
  buildScopeDisplayLabel,
  type ScopeDisplayNames
} from '../../../src/analytics/domain/display-name.domain';
import { buildMarketScope } from '../../../src/analytics/domain/market-scope.domain';
import type { FilterOption } from '../../../src/analytics/domain/filter-option.domain';

/**
 * Golden dataset for US3 catalog display-name resolution (T066). Exercises the
 * pure display-name policy (`displayOrCanonical` + `buildScopeDisplayLabel`)
 * against two fixtures: one WITH catalog display names for make/model, and one
 * WITHOUT any catalog rows. Asserts the exact options + scope label JSON each
 * fixture must produce — locking the canonical-fallback rule (spec edge case 83:
 * the canonical value is used WITHOUT transforming or normalizing it).
 *
 * The Prisma catalog query is covered by the integration test (T062); this
 * golden test pins the resolution policy + label shape so future regressions
 * (e.g. accidental title-casing of the fallback) surface immediately.
 */

interface CanonicalGroup {
  value: string | number;
  count: number;
}

/** Apply the display-name policy to canonical groups using a catalog display map. */
function resolveOptions(
  groups: CanonicalGroup[],
  catalog: Map<string, string | null>
): FilterOption[] {
  return groups.map((g) => ({
    value: g.value,
    displayName: displayOrCanonical(catalog.get(String(g.value).toLowerCase()) ?? null, g.value),
    activeListingCount: g.count
  }));
}

/** Resolve scope display names for a selection using a catalog display map. */
function resolveScopeDisplayNames(
  selection: { make?: string; model?: string; trim?: string; year?: number },
  catalog: { make: Map<string, string | null>; model: Map<string, string | null> }
): ScopeDisplayNames {
  const names: ScopeDisplayNames = {};
  if (selection.make) {
    names.make = displayOrCanonical(catalog.make.get(selection.make.toLowerCase()) ?? null, selection.make);
  }
  if (selection.make && selection.model) {
    names.model = displayOrCanonical(catalog.model.get(selection.model.toLowerCase()) ?? null, selection.model);
  }
  if (selection.make && selection.model && selection.trim) {
    // No catalog trim display — canonical fallback.
    names.trim = displayOrCanonical(null, selection.trim);
  }
  if (selection.make && selection.model && selection.trim && selection.year !== undefined) {
    // No catalog year display — canonical fallback (stringified integer).
    names.year = displayOrCanonical(null, selection.year);
  }
  return names;
}

// Canonical option groups (read-only inputs from the listing repository).
const MAKE_GROUPS: CanonicalGroup[] = [
  { value: 'toyota', count: 4381 },
  { value: 'bmw', count: 2981 }
];
const MODEL_GROUPS: CanonicalGroup[] = [
  { value: 'corolla', count: 842 },
  { value: 'camry', count: 612 }
];
const TRIM_GROUPS: CanonicalGroup[] = [
  { value: 'xli', count: 214 },
  { value: 'gli', count: 120 }
];
const YEAR_GROUPS: CanonicalGroup[] = [
  { value: 2023, count: 57 },
  { value: 2022, count: 31 }
];

describe('US3 catalog display-name fallback golden (T066)', () => {
  it('resolves make/model display names from the catalog and falls back for trim/year', () => {
    const catalog = {
      make: new Map<string, string | null>([
        ['toyota', 'Toyota'],
        ['bmw', 'BMW']
      ]),
      model: new Map<string, string | null>([
        ['corolla', 'Corolla'],
        ['camry', 'Camry']
      ])
    };

    const makes = resolveOptions(MAKE_GROUPS, catalog.make);
    const models = resolveOptions(MODEL_GROUPS, catalog.model);
    const trims = resolveOptions(TRIM_GROUPS, new Map());
    const years = resolveOptions(YEAR_GROUPS, new Map());

    expect(makes).toEqual([
      { value: 'toyota', displayName: 'Toyota', activeListingCount: 4381 },
      { value: 'bmw', displayName: 'BMW', activeListingCount: 2981 }
    ]);
    expect(models).toEqual([
      { value: 'corolla', displayName: 'Corolla', activeListingCount: 842 },
      { value: 'camry', displayName: 'Camry', activeListingCount: 612 }
    ]);
    // Trim: catalog has no trim display → canonical fallback, unchanged.
    expect(trims).toEqual([
      { value: 'xli', displayName: 'xli', activeListingCount: 214 },
      { value: 'gli', displayName: 'gli', activeListingCount: 120 }
    ]);
    // Year: catalog has no year display → canonical fallback (integer stringified).
    expect(years).toEqual([
      { value: 2023, displayName: '2023', activeListingCount: 57 },
      { value: 2022, displayName: '2022', activeListingCount: 31 }
    ]);

    // Scope label at the year level: catalog display names for make+model,
    // canonical fallback for trim+year (no title-casing of "xli").
    const selection = { make: 'toyota', model: 'corolla', trim: 'xli', year: 2023 };
    const scope = buildMarketScope(selection);
    const names = resolveScopeDisplayNames(selection, catalog);
    scope.label = buildScopeDisplayLabel(scope.level, names);
    expect(scope).toEqual({
      level: 'year',
      label: 'Toyota Corolla xli 2023',
      canonical: { make: 'toyota', model: 'corolla', trim: 'xli', year: 2023 }
    });
  });

  it('falls back to canonical values for every level when the catalog has no rows', () => {
    const emptyCatalog = { make: new Map<string, string | null>(), model: new Map<string, string | null>() };

    const makes = resolveOptions(MAKE_GROUPS, emptyCatalog.make);
    const models = resolveOptions(MODEL_GROUPS, emptyCatalog.model);
    const trims = resolveOptions(TRIM_GROUPS, new Map());
    const years = resolveOptions(YEAR_GROUPS, new Map());

    // No catalog rows → every displayName is the canonical value, unchanged.
    expect(makes).toEqual([
      { value: 'toyota', displayName: 'toyota', activeListingCount: 4381 },
      { value: 'bmw', displayName: 'bmw', activeListingCount: 2981 }
    ]);
    expect(models).toEqual([
      { value: 'corolla', displayName: 'corolla', activeListingCount: 842 },
      { value: 'camry', displayName: 'camry', activeListingCount: 612 }
    ]);
    expect(trims).toEqual([
      { value: 'xli', displayName: 'xli', activeListingCount: 214 },
      { value: 'gli', displayName: 'gli', activeListingCount: 120 }
    ]);
    expect(years).toEqual([
      { value: 2023, displayName: '2023', activeListingCount: 57 },
      { value: 2022, displayName: '2022', activeListingCount: 31 }
    ]);

    // Scope label at the year level: pure canonical fallback (no transformation).
    const selection = { make: 'toyota', model: 'corolla', trim: 'xli', year: 2023 };
    const scope = buildMarketScope(selection);
    const names = resolveScopeDisplayNames(selection, emptyCatalog);
    scope.label = buildScopeDisplayLabel(scope.level, names);
    expect(scope).toEqual({
      level: 'year',
      label: 'toyota corolla xli 2023',
      canonical: { make: 'toyota', model: 'corolla', trim: 'xli', year: 2023 }
    });
  });

  it('falls back per-value when only some canonical values have catalog rows', () => {
    // Catalog knows toyota but not bmw; knows corolla but not camry.
    const catalog = {
      make: new Map<string, string | null>([['toyota', 'Toyota']]),
      model: new Map<string, string | null>([['corolla', 'Corolla']])
    };

    const makes = resolveOptions(MAKE_GROUPS, catalog.make);
    const models = resolveOptions(MODEL_GROUPS, catalog.model);

    expect(makes[0]).toEqual({ value: 'toyota', displayName: 'Toyota', activeListingCount: 4381 });
    expect(makes[1]).toEqual({ value: 'bmw', displayName: 'bmw', activeListingCount: 2981 });
    expect(models[0]).toEqual({ value: 'corolla', displayName: 'Corolla', activeListingCount: 842 });
    expect(models[1]).toEqual({ value: 'camry', displayName: 'camry', activeListingCount: 612 });

    // Make-only scope with a partial catalog row: Toyota display for the make.
    const selection = { make: 'toyota' };
    const scope = buildMarketScope(selection);
    const names = resolveScopeDisplayNames(selection, catalog);
    scope.label = buildScopeDisplayLabel(scope.level, names);
    expect(scope).toEqual({ level: 'make', label: 'Toyota', canonical: { make: 'toyota' } });
  });

  it('renders the fixed overall label when no selection is present', () => {
    const scope = buildMarketScope({});
    const names = resolveScopeDisplayNames({}, { make: new Map(), model: new Map() });
    scope.label = buildScopeDisplayLabel(scope.level, names);
    expect(scope).toEqual({ level: 'overall', label: 'Overall UAE Used Cars', canonical: {} });
  });
});