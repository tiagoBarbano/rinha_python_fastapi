CREATE EXTENSION pg_trgm;

CREATE TABLE IF NOT EXISTS pessoa (
    id TEXT NOT NULL CONSTRAINT PK_PESSOAS PRIMARY KEY,
    apelido VARCHAR(32),
    nome VARCHAR(100),
    nascimento DATE,
    stack VARCHAR(1024),
    busca TEXT
);

CREATE  INDEX id_1695417482267_index ON "pessoa" USING btree ("id");

CREATE  INDEX id_21234695417482267_index ON "pessoa" USING btree ("busca");