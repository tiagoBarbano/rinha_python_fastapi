from uuid import uuid4

import asyncpg
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from app.repository.repository import get_db
from app.schema.pessoa import PessoaSchema

router = APIRouter()


@router.post("/pessoas")
async def create(
    pessoa: PessoaSchema,
    conn=Depends(get_db)
): 
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


@router.get("/pessoas/{id}")
async def find_by_id(id: str, conn=Depends(get_db)):
    try:
        
        values = await conn.fetchrow('SELECT * FROM "pessoa" WHERE ID = $1', id)

        if values is None:
            return ORJSONResponse(status_code=404, content="Nao encontrado")

        return ORJSONResponse(status_code=200, content=dict(values))
    except Exception as ex:
        return ORJSONResponse(status_code=400, content=str(ex))


@router.get("/pessoas")
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


@router.get("/contagem-pessoas")
async def count_pessoas(conn=Depends(get_db)):
    values = await conn.fetchrow('SELECT count(*) FROM "pessoa"')

    return ORJSONResponse(status_code=200, content=dict(values))
