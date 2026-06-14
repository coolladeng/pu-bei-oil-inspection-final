"""检查结果API"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.check_result import CheckResult
from app.models.equipment import Equipment, EquipCheckItem
from app.models.check_task import CheckTask
from app.schemas.check_result import CheckResultCreate, CheckResultResponse
from app.security import get_current_user

router = APIRouter()


@router.post("")
async def create_check_result(
    data: CheckResultCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = CheckResult(
        task_id=data.task_id,
        equip_id=data.equip_id,
        item_id=data.item_id,
        user_id=current_user["id"],
        check_time=datetime.now(),
        result_value=data.result_value,
        is_normal=data.is_normal,
        photo_path=data.photo_path,
        remark=data.remark,
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)
    return {"id": result.id, "message": "提交成功"}


@router.get("")
async def list_check_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    task_id: int | None = None,
    equip_id: int | None = None,
    is_normal: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CheckResult).options(
        selectinload(CheckResult.task),
        selectinload(CheckResult.equipment),
        selectinload(CheckResult.check_item),
        selectinload(CheckResult.user),
    )
    if task_id:
        query = query.where(CheckResult.task_id == task_id)
    if equip_id:
        query = query.where(CheckResult.equip_id == equip_id)
    if is_normal is not None:
        query = query.where(CheckResult.is_normal == is_normal)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    query = query.order_by(CheckResult.check_time.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    results = result.scalars().all()

    return {
        "list": [{
            "id": r.id,
            "taskId": r.task_id,
            "taskName": r.task.task_name if r.task else None,
            "equipId": r.equip_id,
            "equipCode": r.equipment.code if r.equipment else None,
            "equipName": r.equipment.name if r.equipment else None,
            "itemId": r.item_id,
            "itemName": r.check_item.item_name if r.check_item else None,
            "itemType": r.check_item.item_type if r.check_item else None,
            "userId": r.user_id,
            "userName": r.user.real_name if r.user else None,
            "checkTime": r.check_time.isoformat() if r.check_time else None,
            "resultValue": r.result_value,
            "isNormal": r.is_normal,
            "photoPath": r.photo_path,
            "remark": r.remark,
        } for r in results],
        "total": total, "page": page, "pageSize": page_size,
    }
