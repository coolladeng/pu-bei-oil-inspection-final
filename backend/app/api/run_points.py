"""巡检点管理API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.run_point import RunPoint
from app.models.dept import SysDept
from app.schemas.run_point import RunPointCreate, RunPointUpdate, RunPointResponse

router = APIRouter()


@router.get("")
async def list_run_points(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: str | None = None,
    dept_id: int | None = None,
    status: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(RunPoint).options(selectinload(RunPoint.dept))
    if name:
        query = query.where(RunPoint.name.like(f"%{name}%"))
    if dept_id:
        query = query.where(RunPoint.dept_id == dept_id)
    if status is not None:
        query = query.where(RunPoint.status == status)

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar() or 0

    query = query.order_by(RunPoint.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    points = result.scalars().all()

    return {
        "list": [RunPointResponse(
            id=p.id, name=p.name, code=p.code, nfc_uid=p.nfc_uid,
            dept_id=p.dept_id, dept_name=p.dept.name if p.dept else None,
            latitude=p.latitude, longitude=p.longitude, address=p.address, status=p.status,
        ) for p in points],
        "total": total, "page": page, "page_size": page_size,
    }


@router.post("")
async def create_run_point(data: RunPointCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(RunPoint).where(RunPoint.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="巡检点编号已存在")
    if data.nfc_uid:
        existing = await db.execute(select(RunPoint).where(RunPoint.nfc_uid == data.nfc_uid))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="NFC标签UID已绑定其他巡检点")
    point = RunPoint(**data.model_dump())
    db.add(point)
    await db.commit()
    await db.refresh(point)
    return {"id": point.id, "message": "创建成功"}


@router.put("/{point_id}")
async def update_run_point(point_id: int, data: RunPointUpdate, db: AsyncSession = Depends(get_db)):
    point = await db.get(RunPoint, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="巡检点不存在")
    update_data = data.model_dump(exclude_none=True)
    if "nfc_uid" in update_data and update_data["nfc_uid"]:
        existing = await db.execute(select(RunPoint).where(RunPoint.nfc_uid == update_data["nfc_uid"], RunPoint.id != point_id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="NFC标签UID已绑定其他巡检点")
    for key, val in update_data.items():
        setattr(point, key, val)
    await db.commit()
    return {"message": "更新成功"}


@router.delete("/{point_id}")
async def delete_run_point(point_id: int, db: AsyncSession = Depends(get_db)):
    point = await db.get(RunPoint, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="巡检点不存在")
    await db.delete(point)
    await db.commit()
    return {"message": "删除成功"}


@router.get("/by-nfc/{nfc_uid}")
async def lookup_by_nfc(nfc_uid: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RunPoint).where(RunPoint.nfc_uid == nfc_uid).options(selectinload(RunPoint.dept)))
    point = result.scalar_one_or_none()
    if not point:
        raise HTTPException(status_code=404, detail="未找到该NFC标签对应的巡检点")
    return RunPointResponse(
        id=point.id, name=point.name, code=point.code, nfc_uid=point.nfc_uid,
        dept_id=point.dept_id, dept_name=point.dept.name if point.dept else None,
        latitude=point.latitude, longitude=point.longitude, address=point.address, status=point.status,
    )

from fastapi import UploadFile, File
import openpyxl

@router.post("/import")
async def import_run_points(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx / .xls 文件")
    try:
        wb = openpyxl.load_workbook(await file.read())
        ws = wb.active
        created, skipped = 0, 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue
            code, name, nfc_uid, dept_name, latitude, longitude, address = (row + (None,) * 7)[:7]
            existing = await db.execute(select(RunPoint).where(RunPoint.code == str(code) if code else None))
            if existing.scalar_one_or_none():
                skipped += 1
                continue
            point = RunPoint(
                code=str(code) if code else None,
                name=str(name) if name else None,
                nfc_uid=str(nfc_uid) if nfc_uid else None,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                address=str(address) if address else None,
                status=1,
            )
            db.add(point)
            created += 1
        await db.commit()
        return {"message": f"导入完成：成功 {created} 条，跳过 {skipped} 条", "created": created, "skipped": skipped}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")