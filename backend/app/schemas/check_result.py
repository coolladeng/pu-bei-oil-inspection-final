from pydantic import BaseModel


class CheckResultCreate(BaseModel):
    task_id: int
    equip_id: int
    item_id: int
    check_time: str
    result_value: str | None = None
    is_normal: int = 1
    photo_path: str | None = None
    remark: str | None = None


class CheckResultResponse(BaseModel):
    id: int
    task_id: int
    equip_id: int
    item_id: int
    user_id: int
    check_time: str
    result_value: str | None = None
    is_normal: int = 1
    remark: str | None = None

    model_config = {"from_attributes": True}
