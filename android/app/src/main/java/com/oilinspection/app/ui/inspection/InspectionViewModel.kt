package com.oilinspection.app.ui.inspection

import android.app.Activity
import android.content.Intent
import android.nfc.NfcAdapter
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.oilinspection.app.data.api.RunRecordSubmit
import com.oilinspection.app.data.local.entity.PendingRecordEntity
import com.oilinspection.app.data.local.entity.RunPointEntity
import com.oilinspection.app.data.repository.InspectionRepository
import com.oilinspection.app.util.NfcHelper
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import javax.inject.Inject

data class InspectionUiState(
    val pointName: String = "",
    val planId: Long? = null,
    val pointId: Long = 0,
    val nfcUid: String? = null,
    val nfcScanned: Boolean = false,
    val nfcMatched: Boolean = false,
    val expectedNfcUid: String? = null,
    val latitude: String? = null,
    val longitude: String? = null,
    val remark: String = "",
    val photoPaths: List<String> = emptyList(),
    val isSubmitting: Boolean = false,
    val isSuccess: Boolean = false,
    val errorMessage: String? = null,
    val submitResult: String? = null,
    val pointDetail: RunPointEntity? = null
)

@HiltViewModel
class InspectionViewModel @Inject constructor(
    private val inspectionRepository: InspectionRepository,
    private val nfcHelper: NfcHelper
) : ViewModel() {

    private val _uiState = MutableStateFlow(InspectionUiState())
    val uiState: StateFlow<InspectionUiState> = _uiState.asStateFlow()

    fun initInspection(planId: Long, pointId: Long, pointName: String) {
        _uiState.update {
            it.copy(planId = planId, pointId = pointId, pointName = pointName)
        }
        loadPointDetail(pointId)
    }

    private fun loadPointDetail(pointId: Long) {
        viewModelScope.launch {
            val result = inspectionRepository.getRunPoints()
            result.fold(
                onSuccess = { points ->
                    val point = points.find { it.id == pointId }
                    if (point != null) {
                        _uiState.update {
                            it.copy(
                                pointDetail = point,
                                expectedNfcUid = point.nfcUid,
                                latitude = point.latitude?.toString(),
                                longitude = point.longitude?.toString()
                            )
                        }
                    }
                },
                onFailure = { /* ignore, detail is optional */ }
            )
        }
    }

    /**
     * 处理 NFC 标签扫描结果
     */
    fun onNfcTagScanned(intent: Intent?) {
        val uid = nfcHelper.readUidFromIntent(intent)
        if (uid != null) {
            val expected = _uiState.value.expectedNfcUid
            _uiState.update {
                it.copy(
                    nfcUid = uid,
                    nfcScanned = true,
                    nfcMatched = expected != null && uid.equals(expected, ignoreCase = true)
                )
            }
        }
    }

    fun onRemarkChange(value: String) {
        _uiState.update { it.copy(remark = value) }
    }

    fun addPhotoPath(path: String) {
        _uiState.update { it.copy(photoPaths = it.photoPaths + path) }
    }

    fun removePhotoPath(path: String) {
        _uiState.update { it.copy(photoPaths = it.photoPaths - path) }
    }

    fun submitRecord() {
        val state = _uiState.value
        if (!state.nfcScanned) {
            _uiState.update { it.copy(errorMessage = "请先使用 NFC 打卡") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isSubmitting = true, errorMessage = null) }

            val now = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
            val record = RunRecordSubmit(
                planId = state.planId,
                pointId = state.pointId,
                checkTime = now,
                nfcUid = state.nfcUid,
                latitude = state.latitude,
                longitude = state.longitude,
                status = "normal",
                remark = state.remark.ifBlank { null },
                photos = state.photoPaths.ifEmpty { null },
                isOffline = 0
            )

            val result = inspectionRepository.submitRecord(record)
            result.fold(
                onSuccess = { id ->
                    _uiState.update {
                        it.copy(
                            isSubmitting = false,
                            isSuccess = true,
                            submitResult = "提交成功！记录 #$id"
                        )
                    }
                },
                onFailure = { error ->
                    // 网络失败：保存到本地离线队列
                    viewModelScope.launch {
                        val pendingRecord = PendingRecordEntity(
                            planId = state.planId,
                            pointId = state.pointId,
                            pointName = state.pointName,
                            checkTime = now,
                            nfcUid = state.nfcUid,
                            latitude = state.latitude,
                            longitude = state.longitude,
                            status = "normal",
                            remark = state.remark.ifBlank { null },
                            photoPaths = state.photoPaths.joinToString(",").ifBlank { null },
                            isSynced = 0
                        )
                        inspectionRepository.savePendingRecord(pendingRecord)
                        _uiState.update {
                            it.copy(
                                isSubmitting = false,
                                isSuccess = true,
                                submitResult = "已离线保存，联网后自动同步"
                            )
                        }
                    }
                }
            )
        }
    }

    fun clearError() {
        _uiState.update { it.copy(errorMessage = null) }
    }
}
