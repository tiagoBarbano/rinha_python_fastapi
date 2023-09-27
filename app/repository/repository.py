import asyncpg
import fastapi

from app.core.config import get_settings

settings = get_settings()


async def create_db_pool():
    return await asyncpg.create_pool(
        database=settings.database_db,
        host=settings.host_db,
        password=settings.password_db,
        user=settings.user_db,
        port=settings.port_db,
        max_size=settings.num_con_pg,
        timeout=60,
    )
    
# Função para obter uma conexão do pool
async def get_db(req: fastapi.Request):
    async with req.app.state.db_pool.acquire() as connection:
        yield connection
        # try:
        #     yield connection
        # finally:
        #     await connection.close()
        