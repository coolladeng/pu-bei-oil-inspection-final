package com.oilinspection.app.di

import android.content.Context
import androidx.room.Room
import com.oilinspection.app.data.api.AuthApi
import com.oilinspection.app.data.api.InspectionApi
import com.oilinspection.app.data.api.RetrofitClient
import com.oilinspection.app.data.local.AppDatabase
import com.oilinspection.app.data.local.dao.PendingRecordDao
import com.oilinspection.app.data.local.dao.RunPlanDao
import com.oilinspection.app.data.local.dao.RunPointDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideAuthApi(): AuthApi = RetrofitClient.authApi

    @Provides
    @Singleton
    fun provideInspectionApi(): InspectionApi = RetrofitClient.inspectionApi

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context.applicationContext,
            AppDatabase::class.java,
            "oil_inspection.db"
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideRunPlanDao(db: AppDatabase): RunPlanDao = db.runPlanDao()

    @Provides
    fun provideRunPointDao(db: AppDatabase): RunPointDao = db.runPointDao()

    @Provides
    fun providePendingRecordDao(db: AppDatabase): PendingRecordDao = db.pendingRecordDao()
}
