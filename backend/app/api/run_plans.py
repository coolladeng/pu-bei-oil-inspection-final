"""巡检计划API"""
from datetime import datetime, date, timedelta
import calendar
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.run_plan import RunPlan
from app.models.run_point import RunPoint
from app.schemas.run_plan import RunPlanGenerate, RunPlanResponse

router = APIRouter()


@router.get("")
async def list_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    month: str | None = None,
    dept_id: int | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(RunPlan).options(selectinload(RunPlan.point), selectinload(RunPlan.dept))
    if month and len(month) == 6:
        year = int(month[:4]); mon = int(month[4:6])
        start = date(year, mon, 1)
        last_day = calendar.monthrange(year, mon)[1]
        end = date(year, mon, last_day)
        query = query.where(and_(RunPlan.plan_date >= start, RunPlan.plan_date <= end))
    if dept_id:
        query = query.where(RunPlan.dept_id == dept_id)
    if status is not None:
        query = query.where(RunPlan.status == status)

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar() or 0

    query = query.order_by(RunPlan.plan_date).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    plans = result.scalars().all()

    return {
        "list": [RunPlanResponse(
            id=p.id, plan_date=str(p.plan_date), point_id=p.point_id,
            point_name=p.point.name if p.point else None,
            dept_id=p.dept_id, dept_name=p.dept.name if p.dept else None,
            shift_type=p.shift_type, status=p.status,
        ) for p in plans],
        "total": total, "page": page, "page_size": page_size,
    }


@router.post("/generate-monthly")
async def generate_monthly(data: RunPlanGenerate, db: AsyncSession = Depends(get_db)):
    year = int(data.year_month[:4])
    mon = int(data.year_month[4:6])
    start = date(year, mon, 1)
    last_day = calendar.monthrange(year, mon)[1]

    point_query = select(RunPoint).where(RunPoint.status == 1)
    if data.dept_ids:
        point_query = point_query.where(RunPoint.dept_id.in_(data.dept_ids))
    points_result = await db.execute(point_query)
    points = points_result.scalars().all()

    if not points:
        raise HTTPException(status_code=400, detail="没有找到启用状态的巡检点")

    created = 0
    for d in range(1, last_day + 1):
        current_date = date(year, mon, d)
        for point in points:
            existing = await db.execute(
                select(RunPlan).where(
                    RunPlan.point_id == point.id,
                    RunPlan.plan_date == current_date,
                )
            )
            if not existing.scalar_one_or_none():
                plan = RunPlan(
                    plan_date=current_date,
                    point_id=point.id,
                    dept_id=point.dept_id,
                    shift_type="day",
                    time_window_start="08:00",
                    time_window_end="18:00",
                    status=0,
                )
                db.add(plan)
                created += 1

    await db.commit()
    return {"message": f"生成成功，共 {created} 条计划", "count": created}


@router.put("/{plan_id}")
async def update_plan(plan_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    plan = await db.get(RunPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    if "status" in data:
        plan.status = data["status"]
    await db.commit()
    return {"message": "更新成功"}

@router.get("/{plan_id}")
async def get_plan_detail(plan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RunPlan).options(selectinload(RunPlan.point), selectinload(RunPlan.dept)).where(RunPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    return {
        "id": plan.id,
        "plan_date": str(plan.plan_date),
        "point_id": plan.point_id,
        "point_name": plan.point.name if plan.point else None,
        "point_code": plan.point.code if plan.point else None,
        "dept_id": plan.dept_id,
        "dept_name": plan.dept.name if plan.dept else None,
        "shift_type": plan.shift_type,
        "time_window_start": plan.time_window_start,
        "time_window_end": plan.time_window_end,
        "status": plan.status,
    }