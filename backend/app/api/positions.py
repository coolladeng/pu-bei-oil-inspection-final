"""岗位管理API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.position import SysPosition
from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse

router = APIRouter()


@router.get("")
async def list_positions(
    dept_id: int | None = None,
    pos_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(SysPosition).options(selectinload(SysPosition.dept))
    if dept_id:
        query = query.where(SysPosition.dept_id == dept_id)
    if pos_type:
        query = query.where(SysPosition.pos_type == pos_type)
    query = query.order_by(SysPosition.id)
    result = await db.execute(query)
    positions = result.scalars().all()
    return {
        "list": [PositionResponse(
            id=p.id, name=p.name, dept_id=p.dept_id,
            dept_name=p.dept.name if p.dept else None,
            pos_type=p.pos_type, status=p.status,
        ) for p in positions],
    }


@router.post("")
async def create_position(data: PositionCreate, db: AsyncSession = Depends(get_db)):
    pos = SysPosition(**data.model_dump())
    db.add(pos)
    await db.commit()
    await db.refresh(pos)
    return {"id": pos.id, "message": "创建成功"}


@router.put("/{pos_id}")
async def update_position(pos_id: int, data: PositionUpdate, db: AsyncSession = Depends(get_db)):
    pos = await db.get(SysPosition, pos_id)
    if not pos:
        raise HTTPException(status_code=404, detail="岗位不存在")
    update_data = data.model_dump(exclude_none=True)
    for key, val in update_data.items():
        setattr(pos, key, val)
    await db.commit()
    return {"message": "更新成功"}


@router.delete("/{pos_id}")
async def delete_position(pos_id: int, db: AsyncSession = Depends(get_db)):
    pos = await db.get(SysPosition, pos_id)
    if not pos:
        raise HTTPException(status_code=404, detail="岗位不存在")
    await db.delete(pos)
    await db.commit()
    return {"message": "删除成功"}
