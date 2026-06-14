"""部门模型 (三级组织架构)
公司 → 大队 → 班组
"""
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
from typing import Optional
import enum


class DeptLevel(int, enum.Enum):
    COMPANY = 1
    BRIGADE = 2
    TEAM = 3


class SysDept(Base, TimestampMixin):
    __tablename__ = "sys_dept"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_dept.id"), nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)

    parent: Mapped[Optional["SysDept"]] = relationship("SysDept", remote_side=[id], back_populates="children", viewonly=True)
    children: Mapped[list["SysDept"]] = relationship("SysDept", back_populates="parent")
    users: Mapped[list["SysUser"]] = relationship("SysUser", back_populates="dept")
    run_points: Mapped[list["RunPoint"]] = relationship("RunPoint", back_populates="dept")
    positions: Mapped[list["SysPosition"]] = relationship("SysPosition", back_populates="dept")
    equipments: Mapped[list["Equipment"]] = relationship("Equipment", back_populates="dept")



