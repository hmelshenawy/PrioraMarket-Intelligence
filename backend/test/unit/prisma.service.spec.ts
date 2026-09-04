import { withPgBouncerCompatibility } from '../../src/db/prisma.service';

describe('Prisma datasource URL', () => {
  it('adds PgBouncer compatibility when the database URL has no pgbouncer parameter', () => {
    expect(withPgBouncerCompatibility('postgresql://user:password@localhost:5432/priora')).toBe(
      'postgresql://user:password@localhost:5432/priora?pgbouncer=true'
    );
  });

  it('preserves existing URL parameters when adding PgBouncer compatibility', () => {
    expect(withPgBouncerCompatibility('postgresql://user:password@localhost:5432/priora?schema=public')).toBe(
      'postgresql://user:password@localhost:5432/priora?schema=public&pgbouncer=true'
    );
  });

  it('does not override an explicitly configured pgbouncer parameter', () => {
    expect(withPgBouncerCompatibility('postgresql://user:password@localhost:5432/priora?pgbouncer=false')).toBe(
      'postgresql://user:password@localhost:5432/priora?pgbouncer=false'
    );
  });
});
