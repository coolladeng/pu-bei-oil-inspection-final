"""APScheduler 定时任务"""
import calendar
from datetime import date, datetime, timedelta
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import async_session_factory
from app.models.run_plan import RunPlan
from app.models.run_point import RunPoint
from app.models.run_record import RunRecord
from app.models.check_task import CheckTask
from app.models.equipment import Equipment
from app.models.hazard import Hazard
from app.websocket_manager import manager

scheduler = AsyncIOScheduler()


async def generate_monthly_plans(year: int = None, month: int = None):
    """每月1日凌晨2点：生成月度巡检计划"""
    today = date.today()
    year = year or today.year
    month = month or today.month
    last_day = calendar.monthrange(year, month)[1]

    async with async_session_factory() as db:
        points = (await db.execute(
            select(RunPoint).where(RunPoint.status == 1)
        )).scalars().all()

        if not points:
            return

        created = 0
        for d in range(1, last_day + 1):
            current_date = date(year, month, d)
            for point in points:
                existing = (await db.execute(
                    select(RunPlan).where(
                        and_(RunPlan.point_id == point.id, RunPlan.plan_date == current_date)
                    )
                )).scalar_one_or_none()
                if not existing:
                    db.add(RunPlan(
                        plan_date=current_date,
                        point_id=point.id,
                        dept_id=point.dept_id,
                        shift_type="day",
                        time_window_start="08:00",
                        time_window_end="18:00",
                        status=0,
                    ))
                    created += 1
        await db.commit()

    print(f"[Scheduler] 月度计划生成完成: {year}-{month:02d}, 新增 {created} 条")


async def check_overdue_plans():
    """每小时30分：标记漏检计划 + 超时计划"""
    now = datetime.now()
    async with async_session_factory() as db:
        # 漏检：当天之前的未检计划
        missed_count = (await db.execute(
            update(RunPlan)
            .where(and_(RunPlan.status == 0, RunPlan.plan_date < now.date()))
            .values(status=3)
        )).rowcount

        # 超时：当天的未检计划，已超出时间窗口
        overdue_count = (await db.execute(
            update(RunPlan)
            .where(and_(RunPlan.status == 0, RunPlan.plan_date == now.date()))
            .values(status=2)
        )).rowcount

        if missed_count or overdue_count:
            await db.commit()

    if missed_count or overdue_count:
        print(f"[Scheduler] 标记漏检 {missed_count} 条, 超时 {overdue_count} 条")


async def check_task_deadlines():
    """每日6点：检查任务截止日期，标记超时"""
    today = date.today()
    async with async_session_factory() as db:
        count = (await db.execute(
            update(CheckTask)
            .where(
                and_(
                    CheckTask.status.in_([0, 1]),
                    CheckTask.deadline.isnot(None),
                    CheckTask.deadline < today,
                )
            )
            .values(status=3)
        )).rowcount
        if count:
            await db.commit()
            print(f"[Scheduler] 标记超时检查任务 {count} 条")


async def check_equipment_status():
    """每日8点：检查设备维保状态，推送告警"""
    async with async_session_factory() as db:
        abnormal_count = (await db.execute(
            select(Equipment).where(Equipment.status.in_([2, 3]))
        )).scalars().all()

        if abnormal_count:
            alert_data = {
                "type": "equipment_alert",
                "message": f"当前有 {len(abnormal_count)} 台设备处于异常状态（维修中/报废）",
                "count": len(abnormal_count),
                "equipments": [{"id": e.id, "code": e.code, "name": e.name, "status": e.status}
                               for e in abnormal_count[:10]],
            }
            try:
                await manager.broadcast_alert(alert_data)
            except Exception:
                pass
            print(f"[Scheduler] 设备状态告警: {len(abnormal_count)} 台异常")


async def check_stale_hazards():
    """每日8点：检查长时间未处理的隐患，推送提醒"""
    async with async_session_factory() as db:
        # 超过3天未审核
        three_days_ago = datetime.now() - timedelta(days=3)
        stale_review = (await db.execute(
            select(Hazard).where(
                and_(
                    Hazard.status.in_(["reported", "reviewing"]),
                    Hazard.created_at < three_days_ago,
                )
            )
        )).scalars().all()

        # 超过7天未处理
        seven_days_ago = datetime.now() - timedelta(days=7)
        stale_handle = (await db.execute(
            select(Hazard).where(
                and_(
                    Hazard.status == "handling",
                    Hazard.updated_at < seven_days_ago,
                )
            )
        )).scalars().all()

        if stale_review or stale_handle:
            alert_data = {
                "type": "stale_hazard_alert",
                "message": f"{len(stale_review)} 条隐患超过3天未审核, {len(stale_handle)} 条超过7天未处理",
                "staleReviewCount": len(stale_review),
                "staleHandleCount": len(stale_handle),
            }
            try:
                await manager.broadcast_alert(alert_data)
            except Exception:
                pass
            print(f"[Scheduler] 隐患积压告警: 审核积压 {len(stale_review)}, 处理积压 {len(stale_handle)}")


def start_scheduler():
    """启动定时任务调度器"""
    # 月度巡检计划生成 — 每月1日凌晨2点
    scheduler.add_job(
        generate_monthly_plans,
        "cron", day=1, hour=2, minute=0,
        id="monthly_plan_generation",
        name="月度巡检计划生成",
    )

    # 超时/漏检检测 — 每小时30分
    scheduler.add_job(
        check_overdue_plans,
        "cron", hour="*", minute=30,
        id="overdue_plan_check",
        name="超时/漏检检测",
    )

    # 任务截止日期检查 — 每日6点
    scheduler.add_job(
        check_task_deadlines,
        "cron", hour=6, minute=0,
        id="task_deadline_check",
        name="任务截止日期检查",
    )

    # 设备状态检查 — 每日8点
    scheduler.add_job(
        check_equipment_status,
        "cron", hour=8, minute=0,
        id="equipment_status_check",
        name="设备状态告警检查",
    )

    # 隐患积压提醒 — 每日8点
    scheduler.add_job(
        check_stale_hazards,
        "cron", hour=8, minute=5,
        id="stale_hazard_check",
        name="隐患积压提醒",
    )

    scheduler.start()
    print("[Scheduler] 定时任务调度器已启动")
    print("  - 月度计划生成: 每月1日 02:00")
    print("  - 超时/漏检检测: 每小时30分")
    print("  - 任务截止日期: 每日 06:00")
    print("  - 设备状态告警: 每日 08:00")
    print("  - 隐患积压提醒: 每日 08:05")
