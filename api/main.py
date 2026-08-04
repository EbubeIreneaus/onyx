import asyncio
from contextlib import asynccontextmanager
from fastapi import Query
from typing import Optional, Annotated
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from arq import Worker
from workers.config import WorkerSettings
from libs.limiter import limiter
from libs.setup import ensure_default_admin_and_tier
from models.db import get_db
from models.redirect import (
    Redirect as RedirectModel,
    RedirectVisitors as RedirectVisitorModel,
)
from setting import settings

from routers.v1.auth import router as auth_router
from routers.v1.client import router as client_router
from routers.v1.admin import router as admin_router
from routers.v1.payment import router as payment_router
from libs.logger import logger

worker_instance: Worker | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_instance
    await ensure_default_admin_and_tier()
    worker_instance = Worker(
        functions=WorkerSettings.functions,
        redis_settings=WorkerSettings.redis_settings,
        queue_name=WorkerSettings.queue_name,
        poll_delay=5
    )
    worker_task = asyncio.create_task(worker_instance.async_run())
    yield
    if worker_instance:
        await worker_instance.close()
    worker_task.cancel()


app = FastAPI(title="Onyx Link Managent & Web Tracking", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{settings.DOMAIN_NAME}",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(client_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")

# app.include_router(auth_router, prefix="", include_in_schema=False)
# app.include_router(client_router, prefix="", include_in_schema=False)


async def execute_resolve(
    request: Request,
    clean_slug: str,
    domain: Optional[str],
    db: AsyncSession,
    user_agent: Optional[str],
    x_forwarded_for: Optional[str],
):
    if domain:
        target_domain = domain.lower().strip()
    else:
        host_header = request.headers.get("host", settings.DOMAIN_NAME)
        host_domain = host_header.split(":")[0].lower().strip()
        target_domain = (
            settings.DOMAIN_NAME
            if host_domain in ("test", "localhost", "127.0.0.1")
            else host_domain
        )

    stmt = select(RedirectModel).where(
        RedirectModel.domain == target_domain,
        RedirectModel.slug == (clean_slug if clean_slug else None),
    )
    redirect_obj = await db.scalar(stmt)

    if not redirect_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination URL not found for given domain and path",
        )

    if redirect_obj.expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This short link has expired",
        )

    if redirect_obj.expired_on:
        now = datetime.now(timezone.utc)
        exp_on = (
            redirect_obj.expired_on
            if redirect_obj.expired_on.tzinfo
            else redirect_obj.expired_on.replace(tzinfo=timezone.utc)
        )
        if now >= exp_on:
            redirect_obj.expired = True
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This short link has expired",
            )

    client_ip = (
        x_forwarded_for.split(",")[0].strip()
        if x_forwarded_for
        else (request.client.host if request.client else "127.0.0.1")
    )

    try:
        from workers.config import get_arq_pool

        arq = await get_arq_pool()
        await arq.enqueue_job(
            "log_redirect_visitor_task",
            str(redirect_obj.redirect_id),
            client_ip,
            user_agent or "",
            _queue_name="onyx",
        )
    except Exception as err:
        logger.warning(
            f"Failed to enqueue visitor tracking worker job for redirect {redirect_obj.redirect_id}: {err}"
        )

    return {
        "destination": redirect_obj.destination,
        "domain": redirect_obj.domain,
        "slug": redirect_obj.slug,
    }


@app.get("/resolve", tags=["Index Resolution"])
@app.get("/api/v1/resolve", tags=["Index Resolution"])
async def resolve_redirect_query(
    request: Request,
    slug: Optional[str] = Query(None),
    key: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    target_slug = (slug or key or "").strip("/").strip()
    return await execute_resolve(
        request, target_slug, domain, db, user_agent, x_forwarded_for
    )


@app.get("/r/{domain}/{slug:path}", tags=["Index Resolution"])
@app.get("/r/{slug:path}", tags=["Index Resolution"])
@app.get("/{slug:path}", tags=["Index Resolution"])
async def resolve_redirect_path(
    request: Request,
    slug: str = "",
    domain: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    target_slug = slug.strip("/").strip()
    return await execute_resolve(
        request, target_slug, domain, db, user_agent, x_forwarded_for
    )
