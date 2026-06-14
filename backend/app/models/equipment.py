"""设备管理模型"""
from sqlalchemy import Integer, String, Float, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Equipment(Base, TimestampMixin):
    """设备档案"""
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_no: Mapped[str] = mapped_column(String(100), nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=True)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_dept.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    install_date: Mapped[Date] = mapped_column(Date, nullable=True)
    qr_code: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=1)
    remark: Mapped[str] = mapped_column(Text, nullable=True)

    dept: Mapped["SysDept"] = relationship("SysDept", back_populates="equipments")
    check_items: Mapped[list["EquipCheckItem"]] = relationship("EquipCheckItem", back_populates="equipment", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Equipment(id={self.id}, code={self.code}, name={self.name})>"


class EquipCheckItem(Base, TimestampMixin):
    """设备检查项"""
    __tablename__ = "equip_check_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equip_id: Mapped[int] = mapped_column(Integer, ForeignKey("equipment.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)
    options: Mapped[str] = mapped_column(Text, nullable=True)
    normal_min: Mapped[float] = mapped_column(Float, nullable=True)
    normal_max: Mapped[float] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    required: Mapped[int] = mapped_column(Integer, default=1)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="check_items")

    def __repr__(self) -> str:
        return f"<EquipCheckItem(id={self.id}, name={self.item_name})>"

