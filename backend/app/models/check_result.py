"""检查结果模型"""
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
from sqlalchemy import Table, Column


# 任务-设备关联表
check_task_equip = Table(
    "check_task_equip",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("check_task.id"), primary_key=True),
    Column("equip_id", Integer, ForeignKey("equipment.id"), primary_key=True),
)


class CheckResult(Base, TimestampMixin):
    """检查结果"""
    __tablename__ = "check_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("check_task.id"), nullable=False)
    equip_id: Mapped[int] = mapped_column(Integer, ForeignKey("equipment.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("equip_check_item.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_user.id"), nullable=False)
    check_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    result_value: Mapped[str] = mapped_column(Text, nullable=True)
    is_normal: Mapped[int] = mapped_column(Integer, default=1)
    photo_path: Mapped[str] = mapped_column(String(500), nullable=True)
    remark: Mapped[str] = mapped_column(Text, nullable=True)

    task: Mapped["CheckTask"] = relationship("CheckTask")
    equipment: Mapped["Equipment"] = relationship("Equipment")
    check_item: Mapped["EquipCheckItem"] = relationship("EquipCheckItem")
    user: Mapped["SysUser"] = relationship("SysUser")

