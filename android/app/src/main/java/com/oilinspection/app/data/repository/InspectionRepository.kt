package com.oilinspection.app.data.repository

import com.oilinspection.app.data.api.InspectionApi
import com.oilinspection.app.data.api.RunPlanItem
import com.oilinspection.app.data.api.RunPointItem
import com.oilinspection.app.data.api.RunRecordSubmit
import com.oilinspection.app.data.local.dao.PendingRecordDao
import com.oilinspection.app.data.local.dao.RunPlanDao
import com.oilinspection.app.data.local.dao.RunPointDao
import com.oilinspection.app.data.local.entity.PendingRecordEntity
import com.oilinspection.app.data.local.entity.RunPlanEntity
import com.oilinspection.app.data.local.entity.RunPointEntity
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class InspectionRepository @Inject constructor(
    private val inspectionApi: InspectionApi,
    private val runPlanDao: RunPlanDao,
    private val runPointDao: RunPointDao,
    private val pendingRecordDao: PendingRecordDao
) {

    suspend fun getTodayPlans(): Result<List<RunPlanItem>> {
        val today = LocalDate.now().format(DateTimeFormatter.ISO_LOCAL_DATE)
        val month = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMM"))
        return try {
            val response = inspectionApi.getRunPlans(month = month, status = 0, pageSize = 500)
            val todayPlans = response.list.filter { it.planDate == today }
            if (response.list.isNotEmpty()) {
                runPlanDao.insertAll(response.list.map { it.toEntity() })
            }
            Result.success(todayPlans)
        } catch (e: Exception) {
            val cached = runPlanDao.getTodayPlans(today)
            if (cached.isNotEmpty()) {
                Result.success(cached.map { it.toItem() })
            } else {
                Result.failure(Exception("网络不可用，且无本地缓存"))
            }
        }
    }

    suspend fun getRunPoints(): Result<List<RunPointEntity>> {
        return try {
            val response = inspectionApi.getRunPoints()
            if (response.list.isNotEmpty()) {
                runPointDao.insertAll(response.list.map { it.toEntity() })
            }
            Result.success(response.list.map { it.toEntity() })
        } catch (e: Exception) {
            val cached = runPointDao.getAll()
            if (cached.isNotEmpty()) Result.success(cached) else Result.failure(e)
        }
    }

    suspend fun getPointByNfcUid(nfcUid: String): RunPointEntity? {
        return runPointDao.getByNfcUid(nfcUid)
    }

    suspend fun submitRecord(record: RunRecordSubmit): Result<Long> {
        return try {
            val response = inspectionApi.submitRecord(record)
            record.planId?.let { runPlanDao.markCompleted(it) }
            Result.success(response.id)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun savePendingRecord(record: PendingRecordEntity) {
        pendingRecordDao.insert(record)
    }

    suspend fun syncPendingRecords(): Int {
        var syncedCount = 0
        val pending = pendingRecordDao.getUnsynced()
        for (record in pending) {
            try {
                val submit = RunRecordSubmit(
                    planId = record.planId, pointId = record.pointId,
                    checkTime = record.checkTime, nfcUid = record.nfcUid,
                    latitude = record.latitude, longitude = record.longitude,
                    status = record.status, remark = record.remark,
                    photos = record.photoPaths?.split(","), isOffline = 1
                )
                if (submitRecord(submit).isSuccess) {
                    pendingRecordDao.markSynced(record.id)
                    syncedCount++
                }
            } catch (_: Exception) { }
        }
        return syncedCount
    }
}

private fun RunPlanItem.toEntity() = RunPlanEntity(
    id = id, planDate = planDate, pointId = pointId, pointName = pointName,
    pointCode = pointCode, deptId = deptId, deptName = deptName,
    shiftType = shiftType, status = status
)

private fun RunPlanEntity.toItem() = RunPlanItem(
    id = id, planDate = planDate, pointId = pointId, pointName = pointName,
    pointCode = pointCode, deptId = deptId, deptName = deptName,
    shiftType = shiftType, status = status
)

private fun RunPointItem.toEntity() = RunPointEntity(
    id = id, name = name, code = code, nfcUid = nfcUid,
    deptId = deptId, deptName = deptName,
    latitude = latitude, longitude = longitude, address = address, status = status
)
