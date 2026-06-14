from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    real_name: str
    password: str
    phone: str | None = None
    dept_id: int | None = None
    role_ids: list[int] = []


class UserUpdate(BaseModel):
    real_name: str | None = None
    phone: str | None = None
    password: str | None = None
    status: int | None = None
    dept_id: int | None = None
    role_ids: list[int] | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str
    employee_no: str | None = None
    phone: str | None = None
    dept_id: int | None = None
    dept_name: str | None = None
    status: int = 1
    roles: list[str] = []
    last_login_at: str | None = None

    model_config = {"from_attributes": True}


class PageResponse(BaseModel):
    list: list
    total: int = 0
    page: int = 1
    page_size: int = 20
