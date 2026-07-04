

INSERT INTO marketplace_source (code, name, country, base_url)
VALUES ('dubizzle_uae', 'Dubizzle UAE', 'UAE', 'https://dubizzle.com')
ON CONFLICT (code) DO NOTHING;

