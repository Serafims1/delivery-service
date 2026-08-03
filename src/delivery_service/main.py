from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from delivery_service.core.config import get_settings
from delivery_service.core.exceptions import ParcelTypeNotFoundError
from delivery_service.routing.v1.router import router as api_router

settings = get_settings()

app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    version="0.1.0",
)


@app.exception_handler(ParcelTypeNotFoundError)
async def parcel_type_not_found_handler(
    request: Request, exc: ParcelTypeNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


app.include_router(api_router)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.app.secret_key,
    same_site="lax",
    https_only=False,
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "application": settings.app.name,
    }
