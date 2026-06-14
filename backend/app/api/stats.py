"""统计分析API"""
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_, case, extract, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.run_plan import RunPlan
from app.models.run_record import RunRecord
from app.models.run_point import RunPoint
from app.models.dept import SysDept
from app.models.equipment import Equipment
from app.models.hazard import Hazard

router = APIRouter()


# ============================================================
# 每日巡检统计 (大屏用)
# ============================================================

@router.get("/dashboard")
@router.get("/daily-run")
async def daily_run_stats(
    date_str: str | None = None,
    dept_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_str) if date_str else date.today()

    plan_query = select(RunPlan).options(
        selectinload(RunPlan.point), selectinload(RunPlan.dept)
    ).where(RunPlan.plan_date == target_date)
    if dept_id:
        plan_query = plan_query.where(RunPlan.dept_id == dept_id)

    result = await db.execute(plan_query)
    plans = result.scalars().all()

    total = len(plans)
    completed = sum(1 for p in plans if p.status == 1)
    overdue = sum(1 for p in plans if p.status == 2)
    missed = sum(1 for p in plans if p.status == 3)
    rate = round(completed / total * 100, 1) if total > 0 else 0

    # 按部门聚合
    dept_stats = {}
    for p in plans:
        name = p.dept.name if p.dept else "未知"
        if name not in dept_stats:
            dept_stats[name] = {"total": 0, "completed": 0, "overdue": 0, "missed": 0}
        dept_stats[name]["total"] += 1
        if p.status == 1:
            dept_stats[name]["completed"] += 1
        elif p.status == 2:
            dept_stats[name]["overdue"] += 1
        elif p.status == 3:
            dept_stats[name]["missed"] += 1

    progress = []
    for name, st in dept_stats.items():
        r = round(st["completed"] / st["total"] * 100, 1) if st["total"] > 0 else 0
        progress.append({
            "deptName": name,
            "total": st["total"],
            "completed": st["completed"],
            "pending": st["total"] - st["completed"],
            "overdue": st["overdue"],
            "missed": st["missed"],
            "rate": r,
        })

    # 设备统计
    equip_normal = (await db.execute(select(func.count()).where(Equipment.status == 1))).scalar() or 0
    equip_maintaining = (await db.execute(select(func.count()).where(Equipment.status == 2))).scalar() or 0
    equip_scrapped = (await db.execute(select(func.count()).where(Equipment.status == 3))).scalar() or 0

    # 活跃隐患数
    hazard_count = (await db.execute(
        select(func.count()).where(Hazard.status.notin_(["closed"]))
    )).scalar() or 0

    # 今日隐患上报数
    today_hazards = (await db.execute(
        select(func.count()).where(
            func.date(Hazard.created_at) == target_date
        )
    )).scalar() or 0

    # 明细
    details = []
    for p in plans[:100]:
        details.append({
            "deptName": p.dept.name if p.dept else "未知",
            "pointName": p.point.name if p.point else "",
            "pointId": p.point_id,
            "status": p.status,
            "statusLabel": ["未检", "已检", "超时", "漏检"][p.status] if 0 <= p.status <= 3 else "未知",
            "planDate": str(p.plan_date),
            "checkTime": "",  # 需从 RunRecord 获取
        })

    return {
        "totalPoints": total,
        "completed": completed,
        "overdue": overdue,
        "missed": missed,
        "rate": rate,
        "equipNormal": equip_normal,
        "equipMaintaining": equip_maintaining,
        "equipScrapped": equip_scrapped,
        "hazardCount": hazard_count,
        "todayHazards": today_hazards,
        "progress": progress,
        "details": details,
    }


# ============================================================
# 巡检统计
# ============================================================

@router.get("/inspection")
async def inspection_stats(
    days: int = Query(7, description="统计天数"),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()

    # 概要
    result = await db.execute(
        select(RunPlan).where(RunPlan.plan_date == today)
    )
    plans = result.scalars().all()
    total = len(plans)
    completed = sum(1 for p in plans if p.status == 1)
    ovedue = sum(1 for p in plans if p.status == 2)
    missed = sum(1 for p in plans if p.status == 3)
    rate = round(completed / total * 100, 1) if total > 0 else 0

    overview = {
        "total": total,
        "completed": completed,
        "overdue": ovedue,
        "missed": missed,
        "rate": rate,
    }

    # 各班组完成率
    dept_result = await db.execute(
        select(
            RunPlan.dept_id,
            func.count(RunPlan.id).label("total"),
            func.sum(case((RunPlan.status == 1, 1), else_=0)).label("completed"),
            func.sum(case((RunPlan.status == 2, 1), else_=0)).label("overdue"),
            func.sum(case((RunPlan.status == 3, 1), else_=0)).label("missed"),
        )
        .where(RunPlan.plan_date == today)
        .group_by(RunPlan.dept_id)
    )
    dept_progress = []
    for row in dept_result:
        dept = await db.get(SysDept, row.dept_id)
        name = dept.name if dept else "未知"
        r = round(row.completed / row.total * 100, 1) if row.total > 0 else 0
        dept_progress.append({
            "deptName": name,
            "total": row.total,
            "completed": row.completed,
            "overdue": row.overdue,
            "missed": row.missed,
            "rate": r,
        })
    dept_progress.sort(key=lambda x: x["rate"], reverse=True)

    # 近N天每日完成率趋势
    trend = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        day_result = await db.execute(
            select(
                func.count(RunPlan.id).label("total"),
                func.sum(case((RunPlan.status == 1, 1), else_=0)).label("completed"),
            ).where(RunPlan.plan_date == d)
        )
        row = day_result.first()
        day_total = row.total or 0
        day_completed = row.completed or 0
        day_rate = round(day_completed / day_total * 100, 1) if day_total > 0 else 0
        trend.append({
            "date": d.isoformat(),
            "total": day_total,
            "completed": day_completed,
            "rate": day_rate,
        })

    # 个人巡检排名 (今日)
    user_result = await db.execute(
        select(
            RunRecord.user_id,
            func.count(RunRecord.id).label("count"),
        )
        .where(func.date(RunRecord.created_at) == today)
        .group_by(RunRecord.user_id)
        .order_by(text("count DESC"))
        .limit(10)
    )
    user_ranking = []
    for row in user_result:
        from app.models.user import SysUser
        user = await db.get(SysUser, row.user_id)
        user_ranking.append({
            "userId": row.user_id,
            "userName": user.real_name if user else "未知",
            "count": row.count,
        })

    return {
        "overview": overview,
        "deptProgress": dept_progress,
        "trend": trend,
        "userRanking": user_ranking,
    }


# ============================================================
# 设备统计
# ============================================================

@router.get("/equipment")
async def equipment_stats(db: AsyncSession = Depends(get_db)):
    # 概要
    normal = (await db.execute(select(func.count()).where(Equipment.status == 1))).scalar() or 0
    maintaining = (await db.execute(select(func.count()).where(Equipment.status == 2))).scalar() or 0
    scrapped = (await db.execute(select(func.count()).where(Equipment.status == 3))).scalar() or 0
    total = normal + maintaining + scrapped
    fault_rate = round((maintaining + scrapped) / total * 100, 1) if total > 0 else 0

    overview = {
        "total": total,
        "normal": normal,
        "maintaining": maintaining,
        "scrapped": scrapped,
        "faultRate": fault_rate,
    }

    # 按类别统计
    cat_result = await db.execute(
        select(
            Equipment.category,
            func.count(Equipment.id).label("count"),
            func.sum(case((Equipment.status == 1, 1), else_=0)).label("normal_count"),
        )
        .group_by(Equipment.category)
    )
    categories = []
    for row in cat_result:
        if row.category:
            categories.append({
                "category": row.category,
                "total": row.count,
                "normal": row.normal_count or 0,
                "abnormal": (row.count or 0) - (row.normal_count or 0),
            })

    # 设备清单
    result = await db.execute(
        select(Equipment).options(selectinload(Equipment.dept)).order_by(Equipment.id)
    )
    equip_list = []
    for e in result.scalars().all():
        equip_list.append({
            "id": e.id,
            "code": e.code,
            "name": e.name,
            "modelNo": e.model_no,
            "deptName": e.dept.name if e.dept else None,
            "status": e.status,
            "statusLabel": {1: "正常", 2: "维修中", 3: "报废"}.get(e.status, "未知"),
            "category": e.category,
            "location": e.location,
        })

    return {
        "overview": overview,
        "categories": categories,
        "list": equip_list,
    }


# ============================================================
# 隐患统计
# ============================================================

@router.get("/hazard")
async def hazard_stats(db: AsyncSession = Depends(get_db)):
    # 概要
    total = (await db.execute(select(func.count()).select_from(Hazard))).scalar() or 0
    reported = (await db.execute(
        select(func.count()).where(Hazard.status.in_(["reported", "reviewing"]))
    )).scalar() or 0
    handling = (await db.execute(
        select(func.count()).where(Hazard.status == "handling")
    )).scalar() or 0
    completed = (await db.execute(
        select(func.count()).where(Hazard.status == "completed")
    )).scalar() or 0
    closed = (await db.execute(
        select(func.count()).where(Hazard.status == "closed")
    )).scalar() or 0

    overview = {
        "total": total,
        "reported": reported,
        "handling": handling,
        "completed": completed,
        "closed": closed,
    }

    # 按紧急程度统计
    urgency_result = await db.execute(
        select(
            Hazard.urgency,
            func.count(Hazard.id).label("count"),
        ).group_by(Hazard.urgency)
    )
    urgency_stats = []
    for row in urgency_result:
        urgency_stats.append({
            "urgency": row.urgency,
            "urgencyLabel": {"normal": "一般", "important": "重要", "urgent": "紧急"}.get(row.urgency, row.urgency),
            "count": row.count,
        })

    # 近12个月趋势
    today = date.today()
    trend = []
    for i in range(11, -1, -1):
        y = today.year
        m = today.month - i
        while m <= 0:
            m += 12
            y -= 1
        month_start = date(y, m, 1)
        if m == 12:
            month_end = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(y, m + 1, 1) - timedelta(days=1)

        reported_count = (await db.execute(
            select(func.count()).where(
                func.date(Hazard.created_at) >= month_start,
                func.date(Hazard.created_at) <= month_end,
            )
        )).scalar() or 0
        closed_count = (await db.execute(
            select(func.count()).where(
                Hazard.status == "closed",
                func.date(Hazard.updated_at) >= month_start,
                func.date(Hazard.updated_at) <= month_end,
            )
        )).scalar() or 0

        trend.append({
            "month": f"{y}-{m:02d}",
            "reported": reported_count,
            "closed": closed_count,
        })

    # 最近隐患明细
    result = await db.execute(
        select(Hazard).options(
            selectinload(Hazard.reporter),
            selectinload(Hazard.point),
            selectinload(Hazard.equipment),
        ).order_by(Hazard.id.desc()).limit(20)
    )
    recent = []
    for h in result.scalars().all():
        recent.append({
            "id": h.id,
            "title": h.title,
            "urgency": h.urgency,
            "urgencyLabel": {"normal": "一般", "important": "重要", "urgent": "紧急"}.get(h.urgency, h.urgency),
            "status": h.status,
            "statusLabel": {"reported": "已上报", "reviewing": "审核中", "handling": "处理中", "completed": "已完成", "closed": "已关闭"}.get(h.status, h.status),
            "reporterName": h.reporter.real_name if h.reporter else None,
            "pointName": h.point.name if h.point else None,
            "equipName": h.equipment.name if h.equipment else None,
            "createdAt": h.created_at.isoformat() if h.created_at else None,
        })

    return {
        "overview": overview,
        "urgencyStats": urgency_stats,
        "trend": trend,
        "recent": recent,
    }
