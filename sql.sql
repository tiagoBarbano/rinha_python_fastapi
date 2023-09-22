CREATE EXTENSION pg_trgm;

CREATE TABLE IF NOT EXISTS pessoa (
    id uuid DEFAULT gen_random_uuid(),
    apelido VARCHAR(32) CONSTRAINT APELIDO_PK PRIMARY KEY,
    nome VARCHAR(100),
    nascimento DATE,
    stack VARCHAR(1024)
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pessoa_busca_gist ON pessoa USING GIST (busca gist_trgm_ops);