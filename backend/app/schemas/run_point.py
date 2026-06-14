from pydantic import BaseModel


class RunPointCreate(BaseModel):
    name: str
    code: str
    nfc_uid: str | None = None
    dept_id: int
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None


class RunPointUpdate(BaseModel):
    name: str | None = None
    nfc_uid: str | None = None
    status: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None


class RunPointResponse(BaseModel):
    id: int
    name: str
    code: str
    nfc_uid: str | None = None
    dept_id: int
    dept_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    status: int = 1

    model_config = {"from_attributes": True}
