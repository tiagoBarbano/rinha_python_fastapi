from uuid import uuid4
from datetime import date
import asyncpg

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
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
    )
    print("Conexao realizada", pool)


async def startup_redis() -> None:
    redis = aioredis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="rinha_cache")


# FastAPI
app = FastAPI(title="Rinha de Back-end 2023")
app.add_event_handler("startup", startup_pg)
app.add_event_handler("startup", startup_redis)


class PessoaSchema(BaseModel):
    apelido: constr(max_length=32)
    nome: constr(max_length=100)
    nascimento: date
    stack: list[constr(max_length=32)] | None


@app.post("/pessoas", status_code=201)
async def create(pessoa: PessoaSchema):
    global pool

    try:
        async with pool.acquire() as conn:
            values = await conn.fetchrow(
                f"""INSERT INTO pessoa (apelido, nome, nascimento, stack) 
                    VALUES ($1, $2, $3, $4) RETURNING *""",
                pessoa.apelido,
                pessoa.nome,
                pessoa.nascimento,
                ",".join(map(str, pessoa.stack)),
            )
            nova_pessoa = dict(values)

            localtion = {"Location": f"/pessoas/{nova_pessoa.get('id')}"}

            return ORJSONResponse(content="Pessoa Incluída", headers=localtion)
    except asyncpg.exceptions.UniqueViolationError as ex:
        raise HTTPException(status_code=422, detail=str(ex))
    except HTTPException as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@cache(expire=60)
@app.get("/pessoas/{id}", status_code=200)
async def find_by_id(id: str):
    global pool
    async with pool.acquire() as conn:
        values = await conn.fetchrow('SELECT * FROM "pessoa" WHERE ID = $1', id)

    if values is None:
        raise HTTPException(status_code=404)

    r = dict(values)
    return r


@cache(expire=60)
@app.get("/pessoas")
async def find_by_term(t: str = Query(..., min_length=1)):
    global pool
    async with pool.acquire() as conn:
        values = await conn.fetchrow(
            f"""
                SELECT id, nome, apelido, stack
                FROM pessoa
                WHERE apelido ILIKE '%{t}%'
                    OR nome ILIKE '%{t}%'
                    OR CAST(stack AS VARCHAR) ILIKE '%{t}%'
                LIMIT 50;
            """
        )
    return values


@app.get("/contagem-pessoas")
async def count_pessoas():
    global pool
    async with pool.acquire() as conn:
        values = await conn.fetchrow('SELECT count(*) FROM "pessoa"')

    return values
