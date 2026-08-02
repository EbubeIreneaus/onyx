from fastapi import APIRouter
from .domain import router as domain_router
from .redirect import router as redirect_router
from .subscription import router as subscription_router
from .api_key import router as api_key_router

router = APIRouter(prefix="/client", tags=["Client"])

router.include_router(domain_router)
router.include_router(redirect_router)
router.include_router(subscription_router)
router.include_router(api_key_router)
