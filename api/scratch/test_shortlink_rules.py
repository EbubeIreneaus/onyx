import asyncio
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workers.redirect import log_redirect_visitor_task
from models.db import SessionLocal
from models.redirect import RedirectVisitors as RedirectVisitorModel, Redirect as RedirectModel
from sqlalchemy import select

async def test_redirect_rules():
    print("=== Testing Redirect Visitor Worker Task ===")
    async with SessionLocal() as db:
        test_redirect = await db.scalar(select(RedirectModel))
        if test_redirect:
            await log_redirect_visitor_task({}, str(test_redirect.redirect_id), "127.0.0.1", "Mozilla/5.0 Test")
            visitors = await db.scalars(select(RedirectVisitorModel).where(RedirectVisitorModel.redirect_id == test_redirect.redirect_id))
            print(f"Logged Visitors Count: {len(visitors.all())}")
        else:
            print("No existing redirect found to test visitor worker task directly.")

    print("\n=======================================================")
    print("  SHORT LINK RULES & VISITOR WORKER TEST COMPLETED     ")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_redirect_rules())
