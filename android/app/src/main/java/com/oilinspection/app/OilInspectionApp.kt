package com.oilinspection.app

import android.app.Application
import com.oilinspection.app.data.api.RetrofitClient
import com.oilinspection.app.data.local.TokenManager
import dagger.hilt.android.HiltAndroidApp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltAndroidApp
class OilInspectionApp : Application() {

    @Inject
    lateinit var tokenManager: TokenManager

    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    override fun onCreate() {
        super.onCreate()

        // 初始化 Retrofit Token 提供者
        RetrofitClient.setTokenProvider {
            runCatching {
                kotlinx.coroutines.runBlocking {
                    tokenManager.accessToken.first()
                }
            }.getOrNull()
        }
    }
}
