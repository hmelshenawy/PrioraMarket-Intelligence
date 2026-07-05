import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

function tsFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((entry) => {
    const path = join(dir, entry);
    return statSync(path).isDirectory() ? tsFiles(path) : path.endsWith('.ts') ? [path] : [];
  });
}

describe('backend marketplace normalization exclusion', () => {
  it('does not contain marketplace alias dictionaries or display reconstruction', () => {
    const src = join(__dirname, '../../src');
    const text = tsFiles(src)
      .map((path) => readFileSync(path, 'utf8'))
      .join('\n');

    expect(text).not.toMatch(/Mercedes[-\s]?Benz/);
    expect(text).not.toMatch(/C[-\s]?Class/);
    expect(text).not.toMatch(/\bVW\b.*Volkswagen|Volkswagen.*\bVW\b/);
    expect(text).not.toMatch(/alias(?:es)?\s*[:=]/i);
  });
});
