from pydantic import BaseModel


class PositionCreate(BaseModel):
    name: str
    dept_id: int
    pos_type: str


class PositionUpdate(BaseModel):
    name: str | None = None
    pos_type: str | None = None
    status: int | None = None


class PositionResponse(BaseModel):
    id: int
    name: str
    dept_id: int
    dept_name: str | None = None
    pos_type: str
    status: int = 1

    model_config = {"from_attributes": True}
