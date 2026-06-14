package com.oilinspection.app.data.api

import com.google.gson.annotations.SerializedName

// ????
data class LoginRequest(
    @SerializedName("username") val username: String,
    @SerializedName("password") val password: String
)

// ????
data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
    @SerializedName("user") val user: UserInfo
)

// ????
data class UserInfo(
    @SerializedName("id") val id: Long,
    @SerializedName("username") val username: String,
    @SerializedName("real_name") val realName: String,
    @SerializedName("phone") val phone: String?,
    @SerializedName("roles") val roles: List<String>?,
    @SerializedName("dept_name") val deptName: String?,
    @SerializedName("dept_id") val deptId: Long?
)

// Upload response
data class UploadResponse(val url: String)
