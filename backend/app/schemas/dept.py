from pydantic import BaseModel


class DeptCreate(BaseModel):
    name: str
    parent_id: int | None = None
    level: int
    sort_order: int = 0


class DeptUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None
    status: int | None = None


class DeptResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None = None
    level: int
    sort_order: int = 0
    status: int = 1
    children: list["DeptResponse"] | None = None

    model_config = {"from_attributes": True}
