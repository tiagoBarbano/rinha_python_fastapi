CREATE EXTENSION pg_trgm;

CREATE TABLE IF NOT EXISTS pessoa (
    id TEXT NOT NULL,
    apelido VARCHAR(32) CONSTRAINT APELIDO_PK PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    nascimento DATE NOT NULL,
    stack VARCHAR(1024),
    busca TEXT NOT NULL
);

CREATE  INDEX id_1695417482267_index ON "pessoa" USING btree ("id");

CREATE  INDEX id_21234695417482267_index ON "pessoa" USING btree ("busca");