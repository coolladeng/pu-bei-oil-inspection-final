"""部门管理API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.dept import SysDept
from app.schemas.dept import DeptCreate, DeptUpdate, DeptResponse

router = APIRouter()


async def build_tree(depts: list[SysDept], parent_id: int | None = None) -> list[dict]:
    result = []
    for d in depts:
        if d.parent_id == parent_id:
            children = await build_tree(depts, d.id)
            item = {"id": d.id, "name": d.name, "parent_id": d.parent_id, "level": d.level, "sort_order": d.sort_order, "status": d.status}
            if children:
                item["children"] = children
            result.append(item)
    result.sort(key=lambda x: (x["sort_order"], x["id"]))
    return result


@router.get("", response_model=list[DeptResponse])
async def list_depts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysDept).order_by(SysDept.sort_order))
    depts = result.scalars().all()
    return await build_tree(depts)


@router.post("")
async def create_dept(data: DeptCreate, db: AsyncSession = Depends(get_db)):
    if data.parent_id:
        parent = await db.get(SysDept, data.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="父部门不存在")
    dept = SysDept(**data.model_dump())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return {"id": dept.id, "message": "创建成功"}


@router.put("/{dept_id}")
async def update_dept(dept_id: int, data: DeptUpdate, db: AsyncSession = Depends(get_db)):
    dept = await db.get(SysDept, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    for key, val in data.model_dump(exclude_none=True).items():
        setattr(dept, key, val)
    await db.commit()
    return {"message": "更新成功"}


@router.delete("/{dept_id}")
async def delete_dept(dept_id: int, db: AsyncSession = Depends(get_db)):
    dept = await db.get(SysDept, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    children = await db.execute(select(SysDept).where(SysDept.parent_id == dept_id))
    if children.scalars().first():
        raise HTTPException(status_code=400, detail="请先删除子部门")
    from app.models.user import SysUser
    users = await db.execute(select(SysUser).where(SysUser.dept_id == dept_id))
    if users.scalars().first():
        raise HTTPException(status_code=400, detail="该部门下存在用户，无法删除")
    await db.delete(dept)
    await db.commit()
    return {"message": "删除成功"}
