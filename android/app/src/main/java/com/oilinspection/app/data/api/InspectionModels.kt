package com.oilinspection.app.data.api

import com.google.gson.annotations.SerializedName

// ========== 巡检计划 ==========
data class RunPlanItem(
    @SerializedName("id") val id: Long,
    @SerializedName("plan_date") val planDate: String,
    @SerializedName("point_id") val pointId: Long,
    @SerializedName("point_name") val pointName: String?,
    @SerializedName("point_code") val pointCode: String? = null,
    @SerializedName("dept_id") val deptId: Long,
    @SerializedName("dept_name") val deptName: String?,
    @SerializedName("shift_type") val shiftType: String,
    @SerializedName("status") val status: Int  // 0=待检, 1=已检
)

data class PlanListResponse(
    @SerializedName("list") val list: List<RunPlanItem>,
    @SerializedName("total") val total: Int,
    @SerializedName("page") val page: Int,
    @SerializedName("page_size") val pageSize: Int
)

// ========== 巡检点 ==========
data class RunPointItem(
    @SerializedName("id") val id: Long,
    @SerializedName("name") val name: String,
    @SerializedName("code") val code: String,
    @SerializedName("nfc_uid") val nfcUid: String?,
    @SerializedName("dept_id") val deptId: Long,
    @SerializedName("dept_name") val deptName: String?,
    @SerializedName("latitude") val latitude: Double?,
    @SerializedName("longitude") val longitude: Double?,
    @SerializedName("address") val address: String?,
    @SerializedName("status") val status: Int
)

data class PointListResponse(
    @SerializedName("list") val list: List<RunPointItem>,
    @SerializedName("total") val total: Int
)

// ========== 巡检记录提交 ==========
data class RunRecordSubmit(
    @SerializedName("plan_id") val planId: Long?,
    @SerializedName("point_id") val pointId: Long,
    @SerializedName("check_time") val checkTime: String,
    @SerializedName("nfc_uid") val nfcUid: String?,
    @SerializedName("latitude") val latitude: String?,
    @SerializedName("longitude") val longitude: String?,
    @SerializedName("status") val status: String = "normal",
    @SerializedName("remark") val remark: String?,
    @SerializedName("photos") val photos: List<String>?,
    @SerializedName("is_offline") val isOffline: Int = 0
)

data class RecordSubmitResponse(
    @SerializedName("id") val id: Long,
    @SerializedName("message") val message: String
)

// ========== 今日记录 ==========
data class TodayRecordItem(
    @SerializedName("id") val id: Long,
    @SerializedName("point_name") val pointName: String?,
    @SerializedName("check_time") val checkTime: String,
    @SerializedName("status") val status: String
)

data class TodayRecordResponse(
    @SerializedName("list") val list: List<TodayRecordItem>
)

// ========== 设备 ==========
data class EquipmentItem(
    @SerializedName("id") val id: Long,
    @SerializedName("code") val code: String?,
    @SerializedName("name") val name: String,
    @SerializedName("model_no") val modelNo: String?,
    @SerializedName("dept_name") val deptName: String?,
    @SerializedName("status") val status: Int,
    @SerializedName("category") val category: String?,
    @SerializedName("location") val location: String?
)

data class EquipmentListResponse(
    @SerializedName("list") val list: List<EquipmentItem>,
    @SerializedName("total") val total: Int,
    @SerializedName("page") val page: Int,
    @SerializedName("pageSize") val pageSize: Int
)

// ========== 隐患 ==========
data class HazardItem(
    @SerializedName("id") val id: Long,
    @SerializedName("title") val title: String,
    @SerializedName("urgency") val urgency: String,
    @SerializedName("status") val status: String,
    @SerializedName("reporter_name") val reporterName: String?,
    @SerializedName("point_name") val pointName: String?,
    @SerializedName("equip_name") val equipName: String?,
    @SerializedName("created_at") val createdAt: String?
)

data class HazardListResponse(
    @SerializedName("list") val list: List<HazardItem>,
    @SerializedName("total") val total: Int,
    @SerializedName("page") val page: Int,
    @SerializedName("pageSize") val pageSize: Int
)

// ========== 用户信息 ==========
data class UserProfile(
    @SerializedName("id") val id: Long,
    @SerializedName("username") val username: String,
    @SerializedName("real_name") val realName: String,
    @SerializedName("dept_id") val deptId: Long?,
    @SerializedName("roles") val roles: List<String>?
)
