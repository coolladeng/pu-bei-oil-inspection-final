package com.oilinspection.app.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "run_plans")
data class RunPlanEntity(
    @PrimaryKey val id: Long,
    val planDate: String,
    val pointId: Long,
    val pointName: String?,
    val pointCode: String?,
    val deptId: Long,
    val deptName: String?,
    val shiftType: String,
    val status: Int,
    val cachedAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "run_points")
data class RunPointEntity(
    @PrimaryKey val id: Long,
    val name: String,
    val code: String,
    val nfcUid: String?,
    val deptId: Long,
    val deptName: String?,
    val latitude: Double?,
    val longitude: Double?,
    val address: String?,
    val status: Int,
    val cachedAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "pending_records")
data class PendingRecordEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val planId: Long?,
    val pointId: Long,
    val pointName: String?,
    val checkTime: String,
    val nfcUid: String?,
    val latitude: String?,
    val longitude: String?,
    val status: String,
    val remark: String?,
    val photoPaths: String?,  // 逗号分隔的本地路径
    val isSynced: Int = 0,    // 0=未同步, 1=已同步
    val createdAt: Long = System.currentTimeMillis()
)
