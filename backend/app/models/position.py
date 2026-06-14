"""岗位模型"""
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class SysPosition(Base, TimestampMixin):
    """岗位表"""
    __tablename__ = "sys_position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_dept.id"), nullable=False)
    pos_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[int] = mapped_column(Integer, default=1)
    remark: Mapped[str] = mapped_column(Text, nullable=True)

    dept: Mapped["SysDept"] = relationship("SysDept", back_populates="positions")

    def __repr__(self) -> str:
        return f"<SysPosition(id={self.id}, name={self.name}, type={self.pos_type})>"

