import asyncio
from app.database import async_session_factory
from sqlalchemy import text

async def fix():
    async with async_session_factory() as db:
        await db.execute(text("UPDATE sys_dept SET name='\u50a8\u8fd0\u9500\u552e\u5206\u516c\u53f8' WHERE id=1"))
        await db.execute(text('UPDATE sys_dept SET parent_id=1 WHERE id=2'))
        await db.execute(text('UPDATE sys_dept SET parent_id=2 WHERE id IN (3,4,5,6,7)'))
        await db.commit()
        
        result = await db.execute(text('SELECT id, name, level, parent_id FROM sys_dept ORDER BY id'))
        for r in result.fetchall():
            print(f'  id={r[0]}, name={r[1]}, level={r[2]}, parent_id={r[3]}')
        
        result2 = await db.execute(text('SELECT id, username, real_name, status FROM sys_user'))
        for r in result2.fetchall():
            print(f'  User: id={r[0]}, username={r[1]}, real_name={r[2]}, status={r[3]}')

asyncio.run(fix())