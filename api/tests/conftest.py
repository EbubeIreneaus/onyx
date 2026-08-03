import asyncio
import importlib
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DOMAIN_NAME", "localhost:3000")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("ONYX_ADMIN_EMAIL", "admin@onyx.com")
os.environ.setdefault("ONYX_ADMIN_PASS", "178420443")
os.environ.setdefault("PAYSTACK_SECRET", "test")
os.environ.setdefault("PAYSTACK_PUBLIC", "test")
os.environ.setdefault("MAIL_USER", "test@example.com")
os.environ.setdefault("MAIL_HOST", "smtp.test")
os.environ.setdefault("MAIL_PASS", "test")
os.environ.setdefault("MAIL_FROM", "test@example.com")
os.environ.setdefault("MAIL_FROM_NAME", "Onyx")
os.environ.setdefault("CLOUDINARY_NAME", "test")
os.environ.setdefault("CLOUDINARY_SECRET", "test")
os.environ.setdefault("CLOUDINARY_KEY", "test")
os.environ.setdefault("STRIPE_SECRET", "test")
os.environ.setdefault("STRIPE_HOOK_SECRET", "test")


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("testdb") / "onyx.sqlite"
    os.environ["DB_URL"] = f"sqlite+aiosqlite:///{db_path}"

    import setting as settings_module
    import models.db as models_db
    import models as models_package

    importlib.reload(settings_module)
    importlib.reload(models_db)

    import models.admin as admin_module
    import models.redirect as redirect_module
    import models.user as user_module
    import libs.setup as setup_module
    import routers.v1.auth as auth_router_module
    import routers.v1.admin as admin_router_module
    import routers.v1.client as client_router_module
    import routers.v1.payment as payment_router_module
    import main as main_module

    importlib.reload(user_module)
    importlib.reload(admin_module)
    importlib.reload(redirect_module)
    importlib.reload(models_package)
    importlib.reload(setup_module)
    importlib.reload(auth_router_module)
    importlib.reload(admin_router_module)
    importlib.reload(client_router_module)
    importlib.reload(payment_router_module)
    importlib.reload(main_module)

    from models.db import Base, engine

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup_db())

    with TestClient(main_module.app) as test_client:
        yield test_client

    async def teardown_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(teardown_db())
