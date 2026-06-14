"""隐患管理API"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.hazard import Hazard, HazardFlow, HazardAttachment
from app.models.user import SysUser
from app.schemas.hazard import HazardCreate, HazardReview, HazardHandle, HazardAccept
from app.security import get_current_user
from app.websocket_manager import manager

router = APIRouter()


@router.post("")
async def create_hazard(
    data: HazardCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    hazard = Hazard(
        title=data.title,
        description=data.description,
        source=data.source,
        source_id=data.source_id,
        point_id=data.point_id,
        equip_id=data.equip_id,
        reporter_id=current_user["id"],
        urgency=data.urgency,
        status="reported",
    )
    db.add(hazard)
    await db.flush()

    # 流转记录
    flow = HazardFlow(
        hazard_id=hazard.id,
        action="report",
        operator_id=current_user["id"],
        to_status="reported",
    )
    db.add(flow)

    # 照片附件
    if data.photos:
        for photo in data.photos:
            db.add(HazardAttachment(hazard_id=hazard.id, file_type="photo", file_path=photo))

    # 视频附件
    if hasattr(data, "videos") and data.videos:
        for video in data.videos:
            db.add(HazardAttachment(hazard_id=hazard.id, file_type="video", file_path=video))

    await db.commit()
    await db.refresh(hazard)

    # WebSocket 推送告警
    try:
        await manager.broadcast_alert({
            "type": "new_hazard",
            "hazardId": hazard.id,
            "title": hazard.title,
            "urgency": hazard.urgency,
            "status": "reported",
        })
    except Exception:
        pass  # 推送失败不影响主流程

    return {"id": hazard.id, "message": "上报成功"}


@router.get("")
async def list_hazards(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    urgency: str | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Hazard).options(
        selectinload(Hazard.reporter),
        selectinload(Hazard.reviewer),
        selectinload(Hazard.handler),
        selectinload(Hazard.point),
        selectinload(Hazard.equipment),
    )
    if status:
        statuses = status.split(",")
        query = query.where(Hazard.status.in_(statuses))
    if urgency:
        query = query.where(Hazard.urgency == urgency)
    if keyword:
        query = query.where(
            or_(Hazard.title.like(f"%{keyword}%"), Hazard.description.like(f"%{keyword}%"))
        )

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar() or 0

    query = query.order_by(Hazard.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    hazards = result.scalars().all()

    return {
        "list": [_serialize_hazard(h) for h in hazards],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


@router.get("/{hazard_id}")
async def get_hazard(hazard_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Hazard)
        .options(
            selectinload(Hazard.reporter),
            selectinload(Hazard.reviewer),
            selectinload(Hazard.handler),
            selectinload(Hazard.point),
            selectinload(Hazard.equipment),
            selectinload(Hazard.attachments),
            selectinload(Hazard.flows).selectinload(HazardFlow.operator),
        )
        .where(Hazard.id == hazard_id)
    )
    hazard = result.scalar_one_or_none()
    if not hazard:
        raise HTTPException(status_code=404, detail="隐患不存在")
    return _serialize_hazard_detail(hazard)


@router.put("/{hazard_id}/review")
async def review_hazard(
    hazard_id: int,
    data: HazardReview,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    hazard = await db.get(Hazard, hazard_id)
    if not hazard:
        raise HTTPException(status_code=404, detail="隐患不存在")
    if hazard.status not in ("reported", "reviewing"):
        raise HTTPException(status_code=400, detail=f"当前状态({hazard.status})不可审核")

    old_status = hazard.status
    if data.action == "approve":
        hazard.status = "handling"
    else:
        hazard.status = "closed"

    hazard.reviewer_id = current_user["id"]
    hazard.review_comment = data.comment

    flow = HazardFlow(
        hazard_id=hazard_id,
        action="review" if data.action == "approve" else "reject",
        operator_id=current_user["id"],
        from_status=old_status,
        to_status=hazard.status,
        comment=data.comment,
    )
    db.add(flow)
    await db.commit()
    return {"message": "审核完成", "status": hazard.status}


@router.put("/{hazard_id}/handle")
async def handle_hazard(
    hazard_id: int,
    data: HazardHandle,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    hazard = await db.get(Hazard, hazard_id)
    if not hazard:
        raise HTTPException(status_code=404, detail="隐患不存在")
    if hazard.status != "handling":
        raise HTTPException(status_code=400, detail=f"当前状态({hazard.status})不可处理")

    old_status = hazard.status
    hazard.status = "completed"
    hazard.handler_id = current_user["id"]
    hazard.handle_result = data.result
    hazard.completed_at = datetime.now()

    flow = HazardFlow(
        hazard_id=hazard_id,
        action="handle",
        operator_id=current_user["id"],
        from_status=old_status,
        to_status="completed",
        comment=data.result,
    )
    db.add(flow)
    await db.commit()
    return {"message": "处理完成", "status": hazard.status}


@router.put("/{hazard_id}/accept")
async def accept_hazard(
    hazard_id: int,
    data: HazardAccept,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    hazard = await db.get(Hazard, hazard_id)
    if not hazard:
        raise HTTPException(status_code=404, detail="隐患不存在")
    if hazard.status != "completed":
        raise HTTPException(status_code=400, detail=f"当前状态({hazard.status})不可验收")

    old_status = hazard.status
    hazard.status = "closed"

    flow = HazardFlow(
        hazard_id=hazard_id,
        action="accept",
        operator_id=current_user["id"],
        from_status=old_status,
        to_status="closed",
        comment=data.comment,
    )
    db.add(flow)
    await db.commit()
    return {"message": "验收完成", "status": hazard.status}


@router.get("/stats/overview")
async def hazard_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count()).select_from(Hazard))
    total = total_result.scalar() or 0

    pending_review_result = await db.execute(
        select(func.count()).where(Hazard.status.in_(["reported", "reviewing"]))
    )
    pending_review = pending_review_result.scalar() or 0

    pending_handle_result = await db.execute(
        select(func.count()).where(Hazard.status == "handling")
    )
    pending_handle = pending_handle_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count()).where(Hazard.status == "completed")
    )
    completed = completed_result.scalar() or 0

    closed_result = await db.execute(
        select(func.count()).where(Hazard.status == "closed")
    )
    closed = closed_result.scalar() or 0

    return {
        "total": total,
        "pendingReview": pending_review,
        "pendingHandle": pending_handle,
        "completed": completed,
        "closed": closed,
    }


# ---- 序列化辅助 ----

def _serialize_hazard(h: Hazard) -> dict:
    return {
        "id": h.id,
        "title": h.title,
        "description": h.description,
        "source": h.source,
        "sourceId": h.source_id,
        "pointId": h.point_id,
        "equipId": h.equip_id,
        "reporterId": h.reporter_id,
        "urgency": h.urgency,
        "status": h.status,
        "reviewerId": h.reviewer_id,
        "handlerId": h.handler_id,
        "reviewComment": h.review_comment,
        "handleResult": h.handle_result,
        "reporterName": h.reporter.real_name if h.reporter else None,
        "reviewerName": h.reviewer.real_name if h.reviewer else None,
        "handlerName": h.handler.real_name if h.handler else None,
        "pointName": h.point.name if h.point else None,
        "equipName": h.equipment.name if h.equipment else None,
        "createdAt": h.created_at.isoformat() if h.created_at else None,
        "updatedAt": h.updated_at.isoformat() if h.updated_at else None,
        "completedAt": h.completed_at.isoformat() if h.completed_at else None,
    }


def _serialize_hazard_detail(h: Hazard) -> dict:
    base = _serialize_hazard(h)
    base["attachments"] = [
        {
            "id": a.id,
            "fileType": a.file_type,
            "filePath": a.file_path,
            "fileSize": a.file_size,
            "duration": a.duration,
        }
        for a in (h.attachments or [])
    ]
    base["flows"] = [
        {
            "id": f.id,
            "action": f.action,
            "operatorId": f.operator_id,
            "operatorName": f.operator.real_name if f.operator else None,
            "fromStatus": f.from_status,
            "toStatus": f.to_status,
            "comment": f.comment,
            "createdAt": f.created_at.isoformat() if f.created_at else None,
        }
        for f in (h.flows or [])
    ]
    return base

