CREATE EXTENSION pg_trgm;

CREATE TABLE IF NOT EXISTS pessoa (
    id uuid,
    apelido VARCHAR(32) CONSTRAINT APELIDO_PK PRIMARY KEY,
    nome VARCHAR(100),
    nascimento DATE,
    stack VARCHAR(1024),
    busca TEXT
);

CREATE  INDEX id_1695417482267_index ON "pessoa" USING btree ("id");

CREATE  INDEX apelido_nome_stack_1695417526647_index ON "pessoa" USING btree ("apelido","nome","stack");

CREATE  INDEX id_21234695417482267_index ON "pessoa" USING btree ("busca");