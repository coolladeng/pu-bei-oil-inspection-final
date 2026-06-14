"""用户管理API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import SysUser, SysRole, user_role
from app.models.dept import SysDept
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PageResponse
from app.security import hash_password

router = APIRouter()


@router.get("", response_model=PageResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: str | None = None,
    dept_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(SysUser).options(selectinload(SysUser.roles), selectinload(SysUser.dept))
    if username:
        query = query.where(SysUser.username.like(f"%{username}%"))
    if dept_id:
        query = query.where(SysUser.dept_id == dept_id)

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar() or 0

    query = query.order_by(SysUser.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return PageResponse(
        list=[UserResponse(
            id=u.id, username=u.username, real_name=u.real_name, employee_no=u.employee_no,
            phone=u.phone, dept_id=u.dept_id, dept_name=u.dept.name if u.dept else None,
            status=u.status, roles=[r.role_name for r in (u.roles or [])],
            last_login_at=str(u.last_login_at) if u.last_login_at else None,
        ) for u in users],
        total=total, page=page, page_size=page_size,
    )


@router.post("")
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(SysUser).where(SysUser.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = SysUser(
        username=data.username,
        real_name=data.real_name,
        password_hash=hash_password(data.password),
        phone=data.phone,
        dept_id=data.dept_id,
    )
    if data.role_ids:
        roles = await db.execute(select(SysRole).where(SysRole.id.in_(data.role_ids)))
        user.roles = roles.scalars().all()

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "message": "创建成功"}


@router.put("/{user_id}")
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await db.get(SysUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = data.model_dump(exclude_none=True, exclude={"password", "role_ids"})
    for key, val in update_data.items():
        setattr(user, key, val)
    if data.password:
        user.password_hash = hash_password(data.password)
    if data.role_ids is not None:
        roles = await db.execute(select(SysRole).where(SysRole.id.in_(data.role_ids)))
        user.roles = roles.scalars().all()

    await db.commit()
    return {"message": "更新成功"}


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(SysUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await db.delete(user)
    await db.commit()
    return {"message": "删除成功"}
