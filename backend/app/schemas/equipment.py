from pydantic import BaseModel


class EquipmentCreate(BaseModel):
    code: str
    name: str
    dept_id: int
    model_no: str | None = None
    manufacturer: str | None = None
    location: str | None = None
    category: str | None = None


class EquipmentUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    dept_id: int | None = None
    model_no: str | None = None
    manufacturer: str | None = None
    location: str | None = None
    category: str | None = None
    status: int | None = None


class EquipmentResponse(BaseModel):
    id: int
    code: str
    name: str
    dept_id: int
    dept_name: str | None = None
    model_no: str | None = None
    manufacturer: str | None = None
    location: str | None = None
    category: str | None = None
    status: int = 1

    model_config = {"from_attributes": True}


class CheckItemCreate(BaseModel):
    item_name: str
    item_type: str  # select / number / text / photo
    options: str | None = None  # JSON for select type
    normal_min: float | None = None
    normal_max: float | None = None
    unit: str | None = None
    sort_order: int = 0
    required: int = 1


class CheckItemUpdate(BaseModel):
    item_name: str | None = None
    item_type: str | None = None
    options: str | None = None
    normal_min: float | None = None
    normal_max: float | None = None
    unit: str | None = None
    sort_order: int | None = None
    required: int | None = None


class CheckItemResponse(BaseModel):
    id: int
    equip_id: int
    item_name: str
    item_type: str
    options: str | None = None
    normal_min: float | None = None
    normal_max: float | None = None
    unit: str | None = None
    sort_order: int = 0
    required: int = 1

    model_config = {"from_attributes": True}
