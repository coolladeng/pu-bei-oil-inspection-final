"""
用户模型 + 角色模型 + 用户角色关联
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Enum, Integer, String, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
import enum


class UserStatus(int, enum.Enum):
    """用户状态"""
    ACTIVE = 1    # 正常
    DISABLED = 0  # 停用


# 用户-角色多对多关联表
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("sys_role.id"), primary_key=True),
)


class SysUser(Base, TimestampMixin):
    """用户表"""
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_dept.id"), nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=UserStatus.ACTIVE)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    dept: Mapped["SysDept"] = relationship("SysDept", back_populates="users")
    roles: Mapped[list["SysRole"]] = relationship(
        "SysRole",
        secondary=user_role,
        back_populates="users",
    )

    def __repr__(self) -> str:
        return f"<SysUser(id={self.id}, username={self.username})>"


class SysRole(Base, TimestampMixin):
    """角色表"""
    __tablename__ = "sys_role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # 关系
    users: Mapped[list["SysUser"]] = relationship(
        "SysUser",
        secondary=user_role,
        back_populates="roles",
    )

    def __repr__(self) -> str:
        return f"<SysRole(id={self.id}, role_name={self.role_name})>"





