"""认证API"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import SysUser, SysRole, user_role
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo, ChangePasswordRequest
from app.security import verify_password, hash_password, create_access_token, get_current_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUser).where(SysUser.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status == 0:
        raise HTTPException(status_code=401, detail="账号已停用")

    # Get roles
    role_result = await db.execute(
        select(SysRole.role_code).join(user_role).where(user_role.c.user_id == user.id)
    )
    roles = [r[0] for r in role_result.all()]

    token = create_access_token({"sub": str(user.id), "username": user.username})
    user.last_login_at = datetime.now()
    await db.commit()

    return LoginResponse(
        access_token=token,
        user=UserInfo(id=user.id, username=user.username, real_name=user.real_name, dept_id=user.dept_id, roles=roles),
    )


@router.get("/profile", response_model=UserInfo)
async def get_profile(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUser).where(SysUser.id == current_user["id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    role_result = await db.execute(
        select(SysRole.role_code).join(user_role).where(user_role.c.user_id == user.id)
    )
    roles = [r[0] for r in role_result.all()]
    return UserInfo(id=user.id, username=user.username, real_name=user.real_name, dept_id=user.dept_id, roles=roles)
