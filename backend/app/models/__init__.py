"""数据模型包 - 注册所有模型"""
from app.models.base import TimestampMixin
from app.models.dept import SysDept, DeptLevel
from app.models.user import SysUser, SysRole, UserStatus, user_role
from app.models.position import SysPosition
from app.models.run_point import RunPoint
from app.models.run_plan import RunPlan
from app.models.run_record import RunRecord
from app.models.equipment import Equipment, EquipCheckItem
from app.models.check_task import CheckTask
from app.models.check_result import CheckResult, check_task_equip
from app.models.hazard import Hazard, HazardAttachment, HazardFlow
from app.models.sys_config import SysConfig

__all__ = [
    "TimestampMixin",
    "SysDept", "DeptLevel",
    "SysUser", "SysRole", "UserStatus", "user_role",
    "SysPosition",
    "RunPoint",
    "RunPlan",
    "RunRecord",
    "Equipment", "EquipCheckItem",
    "CheckTask",
    "CheckResult", "check_task_equip",
    "Hazard", "HazardAttachment", "HazardFlow",
    "SysConfig",
]
