"""检查任务API"""
import json
from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.check_task import CheckTask
from app.models.check_result import check_task_equip
from app.models.equipment import Equipment
from app.models.dept import SysDept
from app.schemas.check_task import CheckTaskCreate, CheckTaskUpdate

router = APIRouter()


@router.get("")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: str | None = None,
    dept_id: int | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CheckTask).options(selectinload(CheckTask.dept))
    if name:
        query = query.where(CheckTask.task_name.like(f"%{name}%"))
    if dept_id:
        query = query.where(CheckTask.dept_id == dept_id)
    if status is not None:
        query = query.where(CheckTask.status == status)

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar() or 0

    query = query.order_by(CheckTask.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tasks = result.scalars().all()

    # Build response with equip_count
    list_data = []
    for t in tasks:
        equip_count_result = await db.execute(
            select(func.count()).select_from(check_task_equip).where(check_task_equip.c.task_id == t.id)
        )
        equip_count = equip_count_result.scalar() or 0
        list_data.append({
            "id": t.id,
            "taskName": t.task_name,
            "deptId": t.dept_id,
            "deptName": t.dept.name if t.dept else None,
            "taskType": t.task_type,
            "frequency": t.frequency,
            "status": t.status,
            "equipCount": equip_count,
            "deadline": str(t.deadline) if t.deadline else None,
        })

    return {"list": list_data, "total": total, "page": page, "pageSize": page_size}


@router.post("")
async def create_task(data: CheckTaskCreate, db: AsyncSession = Depends(get_db)):
    task = CheckTask(
        task_name=data.task_name,
        dept_id=data.dept_id,
        task_type=data.task_type,
        frequency=data.frequency if data.task_type == "regular" else None,
        deadline=date_type.fromisoformat(data.deadline) if data.deadline else None,
    )
    db.add(task)
    await db.flush()

    if data.equip_ids:
        for equip_id in data.equip_ids:
            await db.execute(check_task_equip.insert().values(task_id=task.id, equip_id=equip_id))

    await db.commit()
    await db.refresh(task)
    return {"id": task.id, "message": "创建成功"}


@router.put("/{task_id}")
async def update_task(task_id: int, data: CheckTaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await db.get(CheckTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    update_data = data.model_dump(exclude_none=True)
    equip_ids = update_data.pop("equip_ids", None)

    # Handle deadline conversion
    if "deadline" in update_data:
        dl = update_data["deadline"]
        update_data["deadline"] = date_type.fromisoformat(dl) if dl else None

    for key, val in update_data.items():
        setattr(task, key, val)

    # Update equipment associations if provided
    if equip_ids is not None:
        await db.execute(check_task_equip.delete().where(check_task_equip.c.task_id == task_id))
        for equip_id in equip_ids:
            await db.execute(check_task_equip.insert().values(task_id=task_id, equip_id=equip_id))

    await db.commit()
    return {"message": "更新成功"}


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(CheckTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    await db.execute(check_task_equip.delete().where(check_task_equip.c.task_id == task_id))
    await db.delete(task)
    await db.commit()
    return {"message": "删除成功"}


@router.get("/{task_id}/equipments")
async def list_task_equipments(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Equipment).join(check_task_equip).where(check_task_equip.c.task_id == task_id)
    )
    equipments = result.scalars().all()
    return [{"id": e.id, "code": e.code, "name": e.name} for e in equipments]


# ---- Excel 导入 ----

@router.post("/import")
async def import_tasks(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx / .xls 文件")
    try:
        import openpyxl
        wb = openpyxl.load_workbook(await file.read())
        ws = wb.active
        if not ws:
            raise HTTPException(status_code=400, detail="工作簿为空")
        created, skipped = 0, 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue
            vals = list(row) + [None] * 4
            task_name, dept_name, task_type, frequency = vals[:4]

            if not task_name:
                continue

            # Resolve dept_name to dept_id
            dept_id = None
            if dept_name:
                dept_result = await db.execute(
                    select(SysDept).where(SysDept.name == str(dept_name))
                )
                dept = dept_result.scalar_one_or_none()
                if dept:
                    dept_id = dept.id

            ft = str(frequency).strip() if frequency else None
            if ft and ft not in ("每日", "每周", "每月"):
                ft_map = {"daily": "每日", "weekly": "每周", "monthly": "每月"}
                ft = ft_map.get(ft, ft)

            task = CheckTask(
                task_name=str(task_name),
                dept_id=dept_id or 0,
                task_type="one_time" if str(task_type).strip() == "一次性" else "regular",
                frequency=ft,
            )
            db.add(task)
            created += 1

        await db.commit()
        return {"message": f"导入完成：成功 {created} 条", "created": created, "skipped": skipped}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")
