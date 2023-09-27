import asyncio
import time
from app.repository.repository import create_db_pool
from fastapi import FastAPI, Request, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from app.service import service


def create_app():
    app = FastAPI(
        title="RINHA DE BACKEND - 2023",
        description="RINHA DE BACKEND - 2023",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        debug=False,
    )

    app.add_middleware(GZipMiddleware, minimum_size=10)

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

    @app.middleware("http")
    async def timeout_middleware(request: Request, call_next):
        try:
            start_time = time.time()
            return await asyncio.wait_for(call_next(request), timeout=90)

        except asyncio.TimeoutError:
            process_time = time.time() - start_time
            return ORJSONResponse(
                {
                    "detail": "Request processing time excedeed limit",
                    "processing_time": process_time,
                },
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            )

    app.include_router(service.router, prefix="", tags=["rinha"])

    return app
