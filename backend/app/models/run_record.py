"""巡检记录模型"""
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class RunRecord(Base, TimestampMixin):
    """巡检记录"""
    __tablename__ = "run_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("run_plan.id"), nullable=True)
    point_id: Mapped[int] = mapped_column(Integer, ForeignKey("run_point.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_user.id"), nullable=False)
    check_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    nfc_uid: Mapped[str] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float] = mapped_column(String(30), nullable=True)
    longitude: Mapped[float] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="normal")
    remark: Mapped[str] = mapped_column(Text, nullable=True)
    photos: Mapped[str] = mapped_column(Text, nullable=True)
    is_offline: Mapped[int] = mapped_column(Integer, default=0)
    sync_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    point: Mapped["RunPoint"] = relationship("RunPoint")
    user: Mapped["SysUser"] = relationship("SysUser")
    plan: Mapped["RunPlan"] = relationship("RunPlan")

