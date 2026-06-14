"""角色管理API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import SysRole

router = APIRouter()


@router.get("")
async def list_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysRole).order_by(SysRole.id))
    roles = result.scalars().all()
    return [{"id": r.id, "role_name": r.role_name, "role_code": r.role_code, "description": r.description} for r in roles]


@router.post("")
async def create_role(data: dict, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(SysRole).where(SysRole.role_code == data.get("role_code")))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="角色编码已存在")
    role = SysRole(role_name=data["role_name"], role_code=data["role_code"], description=data.get("description"))
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return {"id": role.id, "message": "创建成功"}


@router.put("/{role_id}")
async def update_role(role_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    role = await db.get(SysRole, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if "role_name" in data:
        role.role_name = data["role_name"]
    if "description" in data:
        role.description = data["description"]
    await db.commit()
    return {"message": "更新成功"}


@router.delete("/{role_id}")
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    role = await db.get(SysRole, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    await db.delete(role)
    await db.commit()
    return {"message": "删除成功"}
