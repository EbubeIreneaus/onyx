import uuid

import qrcode
from sqlalchemy import update
from api.models.db import SessionLocal
from libs.cloudinary import cloudinary_uploader, cloudinary
from libs.logger import logger
from setting import settings
from models.redirect import Redirect as RedirectModel
from .config import get_arq_pool

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)


async def save_qr_to_redirect(ctx, redirect_id, qr_image_url):
    try:
        async with SessionLocal() as session:
            await session.execute(
                update(RedirectModel)
                .where(RedirectModel.redirect_id == redirect_id)
                .values(qr_image=qr_image_url)
            )
            await session.commit()
    except Exception as e:
        logger.error(f"Error occurred while saving QR code to redirect: {e}")
        raise


async def create_and_upload_qr_code(ctx, redirect_id: uuid.UUID, data: str):
    try:
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        upload_result = await cloudinary_uploader.upload(folder=settings.IMAGE_FOLDER)
        url = upload_result["secure_url"]
        await get_arq_pool().enqueue_job(
            "save_qr_to_redirect", redirect_id, url, _queue_name="onyx"
        )
    except Exception as e:
        logger.error(f"Error occurred while creating QR code: {e}")
        raise
