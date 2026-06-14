package com.oilinspection.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.oilinspection.app.data.local.dao.PendingRecordDao
import com.oilinspection.app.data.local.dao.RunPlanDao
import com.oilinspection.app.data.local.dao.RunPointDao
import com.oilinspection.app.data.local.entity.PendingRecordEntity
import com.oilinspection.app.data.local.entity.RunPlanEntity
import com.oilinspection.app.data.local.entity.RunPointEntity

@Database(
    entities = [
        RunPlanEntity::class,
        RunPointEntity::class,
        PendingRecordEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun runPlanDao(): RunPlanDao
    abstract fun runPointDao(): RunPointDao
    abstract fun pendingRecordDao(): PendingRecordDao
}
