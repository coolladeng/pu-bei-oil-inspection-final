from pydantic import BaseModel
from datetime import date


class CheckTaskCreate(BaseModel):
    task_name: str
    dept_id: int
    equip_ids: list[int] = []
    task_type: str = "regular"  # regular / one_time
    frequency: str | None = None  # daily / weekly / monthly
    deadline: str | None = None  # YYYY-MM-DD for one_time tasks


class CheckTaskUpdate(BaseModel):
    task_name: str | None = None
    dept_id: int | None = None
    task_type: str | None = None
    frequency: str | None = None
    deadline: str | None = None
    status: int | None = None
    equip_ids: list[int] | None = None
    remark: str | None = None
