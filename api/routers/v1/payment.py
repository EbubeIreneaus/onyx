import hmac
import hashlib
import json
import logging
from fastapi import APIRouter, Request, HTTPException, Header, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setting import settings
from workers.config import get_arq_pool
from libs.logger import logger

router = APIRouter(prefix="/payments", tags=["Payments & Webhooks"])

@router.post("/paystack-webhook")
async def paystack_webhook(
    request: Request,
    x_paystack_signature: str = Header(None),
):
    body_bytes = await request.body()
    
    if not settings.PAYSTACK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Paystack secret not configured",
        )

    if not x_paystack_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing x-paystack-signature header",
        )

    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET.encode("utf-8"),
        body_bytes,
        hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, x_paystack_signature):
        logger.warning("Received invalid Paystack webhook signature")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    event_type = payload.get("event")
    data = payload.get("data", {})

    logger.info(f"Received Paystack webhook event: {event_type}")

    try:
        arq = await get_arq_pool()
        await arq.enqueue_job("process_paystack_webhook_task", event_type, data, _queue_name="onyx")
    except Exception as e:
        logger.exception(f"Error enqueuing Paystack webhook task: {e}")

    return {"status": "success"}
