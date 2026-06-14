"""巡检计划模型"""
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class RunPlan(Base, TimestampMixin):
    """巡检计划"""
    __tablename__ = "run_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    point_id: Mapped[int] = mapped_column(Integer, ForeignKey("run_point.id"), nullable=False)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_dept.id"), nullable=False)
    shift_type: Mapped[str] = mapped_column(String(20), nullable=False)
    time_window_start: Mapped[str] = mapped_column(String(5), nullable=True)
    time_window_end: Mapped[str] = mapped_column(String(5), nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=0)

    point: Mapped["RunPoint"] = relationship("RunPoint")
    dept: Mapped["SysDept"] = relationship("SysDept")

    def __repr__(self) -> str:
        return f"<RunPlan(id={self.id}, date={self.plan_date}, point={self.point_id})>"

