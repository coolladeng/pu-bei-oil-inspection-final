from pydantic import BaseModel


class RunRecordCreate(BaseModel):
    plan_id: int | None = None
    point_id: int
    check_time: str
    nfc_uid: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    status: str = "normal"
    remark: str | None = None
    photos: list[str] | None = None
    is_offline: int = 0


class RunRecordResponse(BaseModel):
    id: int
    plan_id: int | None = None
    point_id: int
    point_name: str | None = None
    user_id: int
    user_name: str | None = None
    check_time: str
    status: str = "normal"
    remark: str | None = None
    is_offline: int = 0

    model_config = {"from_attributes": True}
