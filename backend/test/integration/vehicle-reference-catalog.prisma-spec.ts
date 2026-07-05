import { readFileSync } from 'node:fs';
import { join } from 'node:path';

describe('Vehicle Reference Catalog Prisma schema compatibility', () => {
  const schema = readFileSync(join(__dirname, '../../prisma/schema.prisma'), 'utf8');

  it('maps vehicle_reference_catalog with display, alias, confidence, and provenance fields', () => {
    expect(schema).toContain('model VehicleReferenceCatalog');
    expect(schema).toContain('@@map("vehicle_reference_catalog")');
    expect(schema).toContain('makeDisplay');
    expect(schema).toContain('modelDisplay');
    expect(schema).toContain('aliases');
    expect(schema).toContain('confidence');
    expect(schema).toContain('sourceFile');
    expect(schema).toContain('sourceRowHash');
    expect(schema).toContain('lastSyncedAt');
  });

  it('does not keep the legacy vehicle_generation_catalog model', () => {
    expect(schema).not.toContain('model vehicle_generation_catalog');
  });
});
