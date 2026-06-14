"""巡检点模型"""
from sqlalchemy import Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class RunPoint(Base, TimestampMixin):
    """巡检点"""
    __tablename__ = "run_point"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nfc_uid: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_dept.id"), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=1)
    remark: Mapped[str] = mapped_column(Text, nullable=True)

    dept: Mapped["SysDept"] = relationship("SysDept", back_populates="run_points")

    def __repr__(self) -> str:
        return f"<RunPoint(id={self.id}, name={self.name}, code={self.code})>"

