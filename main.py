from datetime import date
from uuid import uuid4

import asyncpg
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, constr

from config import get_settings

settings = get_settings()

async def startup_pg():
    global pool
    pool = await asyncpg.create_pool(
        database=settings.database_db,
        host=settings.host_db,
        password=settings.password_db,
        user=settings.user_db,
        port=settings.port_db,
        max_size=150,
        timeout=60
        # max_queries=50000,
    )
    print("Conexao realizada", pool)


app = FastAPI(title="Rinha de Back-end 2023")
app.add_event_handler("startup", startup_pg)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req: Request, exc: RequestValidationError):
    return ORJSONResponse(
        status_code=400,
        content=str(exc.errors()),
    )


class PessoaSchema(BaseModel):
    apelido: constr(max_length=32)
    nome: constr(max_length=100)
    nascimento: date
    stack: list[constr(max_length=32)] | None


@app.post("/pessoas")
async def create(pessoa: PessoaSchema):
    try:
        async with pool.acquire() as conn:
            uudi_id = uuid4()
            values = await conn.fetchrow(
                f"""INSERT INTO pessoa (id, apelido, nome, nascimento, stack, busca) 
                    VALUES ($1, $2, $3, $4, $5, $6)""",
                uudi_id,
                pessoa.apelido,
                pessoa.nome,
                pessoa.nascimento,
                ",".join(map(str, pessoa.stack or [])),
                ",".join(
                    [pessoa.apelido, pessoa.nome] + list(map(str, pessoa.stack or []))
                ),
            )

            return ORJSONResponse(
                status_code=201,
                content="Ok",
                headers={"Location": f"/pessoas/{uudi_id}"},
            )
    except asyncpg.exceptions.UniqueViolationError as ex:
        return ORJSONResponse(status_code=422, content=str(ex))
    except Exception as ex:
        return ORJSONResponse(status_code=400, content=str(ex))


@app.get("/pessoas/{id}", status_code=200)
async def find_by_id(id: str):
    async with pool.acquire() as conn:
        values = await conn.fetchrow('SELECT * FROM "pessoa" WHERE ID = $1', id)

    return ORJSONResponse(status_code=200, content=jsonable_encoder(values))


@app.get("/pessoas")
async def find_by_term(t: str = Query(..., min_length=1)):
    async with pool.acquire() as conn:
        values = await conn.fetchrow(
            f"""
                SELECT id, nome, apelido, stack
                FROM pessoa
                WHERE busca ILIKE '%{t}%'
                LIMIT 50;
            """
        )

    return ORJSONResponse(status_code=200, content=jsonable_encoder(values))


@app.get("/contagem-pessoas")
async def count_pessoas():
    async with pool.acquire() as conn:
        values = await conn.fetchrow('SELECT count(*) FROM "pessoa"')

    return ORJSONResponse(status_code=200, content=jsonable_encoder(values))