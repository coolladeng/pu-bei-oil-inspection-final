from pydantic import BaseModel


class RunPlanGenerate(BaseModel):
    dept_ids: list[int] | None = None
    year_month: str  # e.g. "202606"


class RunPlanResponse(BaseModel):
    id: int
    plan_date: str
    point_id: int
    point_name: str | None = None
    dept_id: int
    dept_name: str | None = None
    shift_type: str
    status: int = 0

    model_config = {"from_attributes": True}
