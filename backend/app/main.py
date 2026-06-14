"""
FastAPI 应用入口
启动命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期: 启动时初始化, 关闭时清理"""
    from app.database import init_db
    try:
        await init_db()
        print("[OK] 数据库表初始化成功")
    except Exception as e:
        print(f"[SKIP] 数据库初始化跳过: {e}")

    yield

    from app.database import close_db
    from app.redis_db import close_redis
    await close_db()
    await close_redis()
    print("[OK] 数据库连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="石油行业巡检与设备管理系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# 注册路由
from app.api.auth import router as auth_router
from app.api.departments import router as dept_router
from app.api.users import router as user_router
from app.api.roles import router as role_router
from app.api.run_points import router as run_point_router
from app.api.positions import router as position_router
from app.api.run_plans import router as run_plan_router
from app.api.run_records import router as run_record_router
from app.api.equipments import router as equipment_router
from app.api.check_tasks import router as check_task_router
from app.api.check_results import router as check_result_router
from app.api.hazards import router as hazard_router
from app.api.uploads import router as upload_router
from app.api.stats import router as stats_router
from app.api.ws import router as ws_router

app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(dept_router, prefix="/api/departments", tags=["组织架构"])
app.include_router(user_router, prefix="/api/users", tags=["用户管理"])
app.include_router(role_router, prefix="/api/roles", tags=["角色管理"])
app.include_router(run_point_router, prefix="/api/run-points", tags=["巡检点管理"])
app.include_router(position_router, prefix="/api/positions", tags=["岗位管理"])
app.include_router(run_plan_router, prefix="/api/run-plans", tags=["巡检计划"])
app.include_router(run_record_router, prefix="/api/run-records", tags=["巡检记录"])
app.include_router(equipment_router, prefix="/api/equipments", tags=["设备管理"])
app.include_router(check_task_router, prefix="/api/check-tasks", tags=["检查任务"])
app.include_router(check_result_router, prefix="/api/check-results", tags=["检查结果"])
app.include_router(hazard_router, prefix="/api/hazards", tags=["隐患管理"])
app.include_router(upload_router, prefix="/api/uploads", tags=["文件上传"])
app.include_router(stats_router, prefix="/api/stats", tags=["统计分析"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
