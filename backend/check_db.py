import asyncio
from app.database import async_session_factory
from sqlalchemy import text

async def check():
    async with async_session_factory() as db:
        # Check the actual schema
        result = await db.execute(text("PRAGMA table_info(sys_user)"))
        for r in result.fetchall():
            print("  col:", r[1], r[2])

        # Check data
        result2 = await db.execute(text("SELECT * FROM sys_user"))
        for r in result2.fetchall():
            print("  row:", r)

asyncio.run(check())
