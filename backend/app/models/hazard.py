"""隐患管理模型"""
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Hazard(Base, TimestampMixin):
    """隐患表"""
    __tablename__ = "hazard"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, nullable=True)
    point_id: Mapped[int] = mapped_column(Integer, ForeignKey("run_point.id"), nullable=True)
    equip_id: Mapped[int] = mapped_column(Integer, ForeignKey("equipment.id"), nullable=True)
    reporter_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_user.id"), nullable=False)
    urgency: Mapped[str] = mapped_column(String(10), default="normal")
    status: Mapped[str] = mapped_column(String(20), default="reported")
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_user.id"), nullable=True)
    handler_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_user.id"), nullable=True)
    review_comment: Mapped[str] = mapped_column(Text, nullable=True)
    handle_result: Mapped[str] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    point: Mapped["RunPoint"] = relationship("RunPoint")
    equipment: Mapped["Equipment"] = relationship("Equipment")
    reporter: Mapped["SysUser"] = relationship("SysUser", foreign_keys=[reporter_id])
    reviewer: Mapped["SysUser"] = relationship("SysUser", foreign_keys=[reviewer_id])
    handler: Mapped["SysUser"] = relationship("SysUser", foreign_keys=[handler_id])
    attachments: Mapped[list["HazardAttachment"]] = relationship("HazardAttachment", back_populates="hazard", cascade="all, delete-orphan")
    flows: Mapped[list["HazardFlow"]] = relationship("HazardFlow", back_populates="hazard", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Hazard(id={self.id}, title={self.title}, status={self.status})>"


class HazardAttachment(Base, TimestampMixin):
    """隐患附件"""
    __tablename__ = "hazard_attachment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hazard_id: Mapped[int] = mapped_column(Integer, ForeignKey("hazard.id"), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)

    hazard: Mapped["Hazard"] = relationship("Hazard", back_populates="attachments")


class HazardFlow(Base, TimestampMixin):
    """隐患流转记录"""
    __tablename__ = "hazard_flow"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hazard_id: Mapped[int] = mapped_column(Integer, ForeignKey("hazard.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_user.id"), nullable=False)
    from_status: Mapped[str] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    hazard: Mapped["Hazard"] = relationship("Hazard", back_populates="flows")
    operator: Mapped["SysUser"] = relationship("SysUser")

