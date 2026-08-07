from arq.connections import RedisSettings
from arq.worker import create_pool
from setting import settings
from .auth import update_session, send_welcome_email
from .paystack import create_paystack_customer_task, sync_paystack_plan_task, process_paystack_webhook_task
from .redirect import log_redirect_visitor_task
from .qr import create_and_upload_qr_code, save_qr_to_redirect, delete_qr_image
from .domain import add_domain_alias, delete_domain_alias
REDIS_SETTING = RedisSettings.from_dsn(settings.REDIS_URL)

async def get_arq_pool():
    pool = await create_pool(REDIS_SETTING)
    return pool

class WorkerSettings:
    functions = [
        update_session,
        send_welcome_email,
        create_paystack_customer_task,
        sync_paystack_plan_task,
        process_paystack_webhook_task,
        log_redirect_visitor_task,
        create_and_upload_qr_code,
        save_qr_to_redirect,
        delete_qr_image,
        add_domain_alias,
        delete_domain_alias
    ]
    redis_settings = REDIS_SETTING
    queue_name = "onyx"