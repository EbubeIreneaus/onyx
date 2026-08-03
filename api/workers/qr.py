import asyncio
import io
import uuid

import qrcode
from sqlalchemy import update
from models.db import SessionLocal
from libs.cloudinary import cloudinary_uploader
from libs.logger import logger
from setting import settings
from models.redirect import Redirect as RedirectModel

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
    from .config import get_arq_pool
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        upload_result = await asyncio.to_thread(
            cloudinary_uploader.upload,
            file=buffer,
            public_id=f"{settings.IMAGE_FOLDER}/{redirect_id}",
            overwrite=True,
        )
        url = upload_result["secure_url"]

        pool = await get_arq_pool()
        await pool.enqueue_job("save_qr_to_redirect", str(redirect_id), url, _queue_name="onyx")
    except Exception as e:
        logger.error(f"Error occurred while creating QR code: {e}")
        raise


async def delete_qr_image(ctx, redirect_id: uuid.UUID):
    try:
        await asyncio.to_thread(
            cloudinary_uploader.destroy,
            public_id=f"{settings.IMAGE_FOLDER}/{redirect_id}"
        )
    except Exception as e:
        logger.error(f"Error occurred while deleting QR image: {e}")
        raise