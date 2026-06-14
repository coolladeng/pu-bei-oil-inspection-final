"""检查任务模型"""
from datetime import datetime, date
from sqlalchemy import Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class CheckTask(Base, TimestampMixin):
    """检查任务"""
    __tablename__ = "check_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_dept.id"), nullable=False)
    task_type: Mapped[str] = mapped_column(String(20), default="regular")
    frequency: Mapped[str] = mapped_column(String(20), nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=0)
    remark: Mapped[str] = mapped_column(Text, nullable=True)

    dept: Mapped["SysDept"] = relationship("SysDept")

    def __repr__(self) -> str:
        return f"<CheckTask(id={self.id}, name={self.task_name})>"

