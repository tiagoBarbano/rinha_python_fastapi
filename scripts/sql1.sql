CREATE EXTENSION pg_trgm;

CREATE TABLE
    IF NOT EXISTS pessoa (
        id TEXT NOT NULL CONSTRAINT PK_PESSOAS PRIMARY KEY,
        apelido VARCHAR(32),
        nome VARCHAR(100),
        nascimento DATE,
        stack TEXT,
        busca TEXT
    );

CREATE INDEX
    CONCURRENTLY IF NOT EXISTS idx_people_trigram ON pessoa USING gist (
        busca gist_trgm_ops(siglen = 64)
    );