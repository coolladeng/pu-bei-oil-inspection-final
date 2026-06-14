from pydantic import BaseModel


class HazardCreate(BaseModel):
    title: str
    description: str | None = None
    source: str = "patrol"  # patrol / check
    source_id: int | None = None
    point_id: int | None = None
    equip_id: int | None = None
    urgency: str = "normal"  # normal / important / urgent
    photos: list[str] | None = None
    videos: list[str] | None = None


class HazardReview(BaseModel):
    comment: str
    action: str = "approve"  # approve / reject


class HazardHandle(BaseModel):
    result: str
    photos: list[str] | None = None  # post-handling photos


class HazardAccept(BaseModel):
    comment: str | None = None
