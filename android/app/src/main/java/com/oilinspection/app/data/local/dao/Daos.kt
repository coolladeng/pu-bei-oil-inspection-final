package com.oilinspection.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.oilinspection.app.data.local.entity.PendingRecordEntity
import com.oilinspection.app.data.local.entity.RunPlanEntity
import com.oilinspection.app.data.local.entity.RunPointEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface RunPlanDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(plans: List<RunPlanEntity>)

    @Query("SELECT * FROM run_plans WHERE planDate = :date ORDER BY pointName ASC")
    suspend fun getTodayPlans(date: String): List<RunPlanEntity>

    @Query("UPDATE run_plans SET status = 1 WHERE id = :planId")
    suspend fun markCompleted(planId: Long)

    @Query("DELETE FROM run_plans WHERE planDate < :beforeDate")
    suspend fun cleanOld(beforeDate: String)
}

@Dao
interface RunPointDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(points: List<RunPointEntity>)

    @Query("SELECT * FROM run_points WHERE id = :id")
    suspend fun getById(id: Long): RunPointEntity?

    @Query("SELECT * FROM run_points WHERE nfcUid = :nfcUid LIMIT 1")
    suspend fun getByNfcUid(nfcUid: String): RunPointEntity?

    @Query("SELECT * FROM run_points ORDER BY name ASC")
    suspend fun getAll(): List<RunPointEntity>
}

@Dao
interface PendingRecordDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(record: PendingRecordEntity)

    @Query("SELECT * FROM pending_records WHERE isSynced = 0 ORDER BY createdAt ASC")
    suspend fun getUnsynced(): List<PendingRecordEntity>

    @Query("UPDATE pending_records SET isSynced = 1 WHERE id = :recordId")
    suspend fun markSynced(recordId: Long)

    @Query("DELETE FROM pending_records WHERE isSynced = 1 AND createdAt < :before")
    suspend fun cleanSynced(before: Long)
}
