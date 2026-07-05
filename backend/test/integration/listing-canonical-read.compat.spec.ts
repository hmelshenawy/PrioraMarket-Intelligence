import { readFileSync } from 'node:fs';
import { join } from 'node:path';

import { SearchQueryBuilder } from '../../src/search/search-query.builder';

describe('Listing canonical read compatibility', () => {
  it('filters by persisted canonical keys without backend normalization', () => {
    const query = new SearchQueryBuilder().buildListingSearchQuery({
      make: 'mercedesbenz',
      model: 'cclass',
      page: 1,
      limit: 20,
      sort: 'newest'
    });

    expect(query.where).toMatchObject({
      make: { equals: 'mercedesbenz', mode: 'insensitive' },
      model: { equals: 'cclass', mode: 'insensitive' }
    });
  });

  it('does not define marketplace normalization dictionaries in backend search code', () => {
    const repository = readFileSync(
      join(__dirname, '../../src/search/listing-read.repository.ts'),
      'utf8'
    );
    const service = readFileSync(join(__dirname, '../../src/search/search.service.ts'), 'utf8');

    expect(repository + service).not.toMatch(/Mercedes\s*Benz|Mercedes-Benz|C\s*Class|C-Class/);
  });
});
