from datetime import date
from uuid import uuid4

import asyncpg
from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, constr

from app.repository.core.config import get_settings

settings = get_settings()


app = FastAPI(title="Rinha de Back-end 2023")
app.add_middleware(GZipMiddleware, minimum_size=100)


async def create_db_pool():
    return await asyncpg.create_pool(
        database=settings.database_db,
        host=settings.host_db,
        password=settings.password_db,
        user=settings.user_db,
        port=settings.port_db,
        max_size=settings.num_con_pg,
        timeout=30,
    )


# Função para obter uma conexão do pool
async def get_db():
    async with app.state.db_pool.acquire() as connection:
        yield connection


@app.on_event("startup")
async def startup_db():
    app.state.db_pool = await create_db_pool()


@app.on_event("shutdown")
async def shutdown_db():
    await app.state.db_pool.close()


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
async def create(pessoa: PessoaSchema, conn=Depends(get_db)):
    try:
        uudi_id = str(uuid4())

        exist = await conn.fetchrow(
            'SELECT ID FROM "pessoa" WHERE APELIDO = $1', pessoa.apelido
        )

        if exist:
            del pessoa
            return ORJSONResponse(status_code=422, content="pessoa existente")

        stack = [] if pessoa.stack is None else list(pessoa.stack)
        await conn.fetchrow(
            """INSERT INTO pessoa (id, apelido, nome, nascimento, stack, busca) 
                VALUES ($1, $2, $3, $4, $5, $6)""",
            uudi_id,
            pessoa.apelido,
            pessoa.nome,
            pessoa.nascimento,
            ",".join(stack),
            ",".join([pessoa.apelido, pessoa.nome] + stack),
        )

        del pessoa

        return ORJSONResponse(
            status_code=201,
            content="Ok",
            headers={"Location": f"/pessoas/{uudi_id}"},
        )
    except asyncpg.exceptions.ConnectionFailureError as ex:
        return ORJSONResponse(status_code=422, content=str(ex))
    except Exception as ex:
        return ORJSONResponse(status_code=400, content=str(ex))


@app.get("/pessoas/{id}")
async def find_by_id(id: str, conn=Depends(get_db)):
    try:
        values = await conn.fetchrow('SELECT * FROM "pessoa" WHERE ID = $1', id)

        if values is None:
            return ORJSONResponse(status_code=404, content="Nao encontrado")

        return ORJSONResponse(status_code=200, content=dict(values))
    except Exception as ex:
        return ORJSONResponse(status_code=400, content=str(ex))


@app.get("/pessoas")
async def find_by_term(t: str = Query(..., min_length=1), conn=Depends(get_db)):
    records = await conn.fetch(
        f"""
            SELECT id, nome, apelido, stack
            FROM pessoa
            WHERE busca ILIKE '%{t}%'
            LIMIT 50;
        """
    )

    return ORJSONResponse(status_code=200, content=[dict(record) for record in records])


@app.get("/contagem-pessoas")
async def count_pessoas(conn=Depends(get_db)):
    values = await conn.fetchrow('SELECT count(*) FROM "pessoa"')

    return ORJSONResponse(status_code=200, content=dict(values))
