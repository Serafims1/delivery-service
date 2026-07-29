from fastapi import APIRouter

from delivery_service.routing.v1.parcel_types import router as parcel_type_router

router = APIRouter(prefix="/api/v1")

router.include_router(parcel_type_router)
