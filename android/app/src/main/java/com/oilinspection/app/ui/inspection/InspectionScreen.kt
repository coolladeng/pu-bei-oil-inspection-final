package com.oilinspection.app.ui.inspection

import android.app.Activity
import android.nfc.NfcAdapter
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Nfc
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.oilinspection.app.ui.theme.DangerRed
import com.oilinspection.app.ui.theme.DarkBackground
import com.oilinspection.app.ui.theme.DarkCard
import com.oilinspection.app.ui.theme.DarkSurface
import com.oilinspection.app.ui.theme.DividerDark
import com.oilinspection.app.ui.theme.InputBackground
import com.oilinspection.app.ui.theme.InputBorder
import com.oilinspection.app.ui.theme.PrimaryCyan
import com.oilinspection.app.ui.theme.SuccessGreen
import com.oilinspection.app.ui.theme.TextMuted
import com.oilinspection.app.ui.theme.TextPrimary
import com.oilinspection.app.ui.theme.TextSecondary
import com.oilinspection.app.ui.theme.WarningAmber
import java.io.File

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InspectionScreen(
    planId: Long,
    pointId: Long,
    pointName: String,
    onBack: () -> Unit,
    onCompleted: () -> Unit,
    viewModel: InspectionViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val nfcAdapter = remember { NfcAdapter.getDefaultAdapter(context) }

    LaunchedEffect(planId, pointId) {
        viewModel.initInspection(planId, pointId, pointName)
    }

    // 处理 NFC Intent (来自 MainActivity.onNewIntent)
    LaunchedEffect(Unit) {
        val activity = context as? Activity
        activity?.intent?.let { intent ->
            if (NfcAdapter.ACTION_TECH_DISCOVERED == intent.action ||
                NfcAdapter.ACTION_TAG_DISCOVERED == intent.action) {
                viewModel.onNfcTagScanned(intent)
            }
        }
    }

    Scaffold(
        containerColor = DarkBackground,
        topBar = {
            TopAppBar(
                title = { Text("巡检打卡", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = TextPrimary) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回", tint = TextPrimary)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = DarkSurface,
                    titleContentColor = TextPrimary
                )
            )
        }
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues)) {
            if (uiState.isSuccess) {
                SuccessContent(
                    message = uiState.submitResult ?: "提交成功",
                    onBack = onCompleted
                )
            } else {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    PointInfoCard(pointName = uiState.pointName, pointDetail = uiState.pointDetail)

                    NfcScanSection(
                        isScanned = uiState.nfcScanned,
                        isMatched = uiState.nfcMatched,
                        nfcUid = uiState.nfcUid,
                        expectedUid = uiState.expectedNfcUid,
                        isNfcAvailable = nfcAdapter != null,
                        isNfcEnabled = nfcAdapter?.isEnabled == true
                    )

                    RemarkSection(
                        remark = uiState.remark,
                        onRemarkChange = viewModel::onRemarkChange
                    )

                    PhotoSection(
                        photoPaths = uiState.photoPaths,
                        onAddPhoto = viewModel::addPhotoPath,
                        onRemovePhoto = viewModel::removePhotoPath
                    )

                    AnimatedVisibility(visible = uiState.errorMessage != null) {
                        Card(
                            colors = CardDefaults.cardColors(containerColor = DangerRed.copy(alpha = 0.1f)),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(Icons.Filled.Error, null, tint = DangerRed, modifier = Modifier.size(20.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(uiState.errorMessage ?: "", color = DangerRed, style = MaterialTheme.typography.bodyMedium)
                            }
                        }
                    }

                    Button(
                        onClick = viewModel::submitRecord,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(52.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = PrimaryCyan,
                            contentColor = DarkBackground,
                            disabledContainerColor = PrimaryCyan.copy(alpha = 0.3f)
                        ),
                        enabled = !uiState.isSubmitting && uiState.nfcScanned
                    ) {
                        if (uiState.isSubmitting) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = DarkBackground,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Icon(Icons.Filled.Send, null, modifier = Modifier.size(20.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("提交巡检记录", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun PointInfoCard(pointName: String, pointDetail: com.oilinspection.app.data.local.entity.RunPointEntity?) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        shape = RoundedCornerShape(14.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Text("巡检点", color = TextMuted, style = MaterialTheme.typography.bodySmall)
            Spacer(modifier = Modifier.height(4.dp))
            Text(pointName, color = TextPrimary, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)

            if (pointDetail != null) {
                Spacer(modifier = Modifier.height(12.dp))
                HorizontalDivider(color = DividerDark)
                Spacer(modifier = Modifier.height(12.dp))

                pointDetail.address?.let { addr ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.LocationOn, null, tint = PrimaryCyan, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(addr, color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
                    }
                    Spacer(modifier = Modifier.height(6.dp))
                }

                pointDetail.nfcUid?.let { uid ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.Nfc, null, tint = PrimaryCyan, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("NFC: $uid", color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
    }
}

@Composable
private fun NfcScanSection(
    isScanned: Boolean,
    isMatched: Boolean,
    nfcUid: String?,
    expectedUid: String?,
    isNfcAvailable: Boolean,
    isNfcEnabled: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = when {
                isScanned && isMatched -> SuccessGreen.copy(alpha = 0.12f)
                isScanned && !isMatched -> DangerRed.copy(alpha = 0.12f)
                else -> DarkCard
            }
        ),
        shape = RoundedCornerShape(14.dp),
        border = if (isScanned && isMatched)
            BorderStroke(1.dp, SuccessGreen.copy(alpha = 0.4f))
        else null
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(72.dp)
                    .clip(CircleShape)
                    .background(
                        when {
                            isScanned && isMatched -> SuccessGreen.copy(alpha = 0.15f)
                            isScanned && !isMatched -> DangerRed.copy(alpha = 0.15f)
                            else -> PrimaryCyan.copy(alpha = 0.15f)
                        }
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = when {
                        isScanned && isMatched -> Icons.Filled.CheckCircle
                        isScanned && !isMatched -> Icons.Filled.Warning
                        else -> Icons.Filled.Nfc
                    },
                    contentDescription = null,
                    tint = when {
                        isScanned && isMatched -> SuccessGreen
                        isScanned && !isMatched -> DangerRed
                        else -> PrimaryCyan
                    },
                    modifier = Modifier.size(36.dp)
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            when {
                !isNfcAvailable -> {
                    Text("设备不支持 NFC", color = DangerRed, fontWeight = FontWeight.Bold)
                    Text("请使用支持 NFC 的设备", color = TextMuted, style = MaterialTheme.typography.bodySmall)
                }
                !isNfcEnabled -> {
                    Text("NFC 未开启", color = WarningAmber, fontWeight = FontWeight.Bold)
                    Text("请在设置中开启 NFC 功能", color = TextMuted, style = MaterialTheme.typography.bodySmall)
                }
                isScanned && isMatched -> {
                    Text("NFC 打卡成功", color = SuccessGreen, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                    Text(nfcUid ?: "", color = TextSecondary, style = MaterialTheme.typography.bodySmall)
                }
                isScanned && !isMatched -> {
                    Text("NFC 不匹配!", color = DangerRed, fontWeight = FontWeight.Bold)
                    Text("期望: ${expectedUid.orEmpty()}", color = TextMuted, style = MaterialTheme.typography.bodySmall)
                    Text("扫描: ${nfcUid.orEmpty()}", color = TextMuted, style = MaterialTheme.typography.bodySmall)
                }
                else -> {
                    Text("请将设备靠近 NFC 标签", color = TextPrimary, fontWeight = FontWeight.Bold)
                    Text("自动识别巡检点", color = TextMuted, style = MaterialTheme.typography.bodySmall)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("期望标签: ${expectedUid ?: "任意"}", color = TextMuted, style = MaterialTheme.typography.bodySmall, fontSize = 11.sp)
                }
            }
        }
    }
}

@Composable
private fun RemarkSection(remark: String, onRemarkChange: (String) -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        shape = RoundedCornerShape(14.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("巡检备注", color = TextMuted, style = MaterialTheme.typography.bodySmall)
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedTextField(
                value = remark,
                onValueChange = onRemarkChange,
                placeholder = { Text("输入巡检情况描述（选填）", color = TextMuted) },
                modifier = Modifier.fillMaxWidth(),
                minLines = 3,
                maxLines = 5,
                shape = RoundedCornerShape(10.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = TextPrimary,
                    unfocusedTextColor = TextPrimary,
                    cursorColor = PrimaryCyan,
                    focusedBorderColor = InputBorder,
                    unfocusedBorderColor = InputBorder,
                    focusedContainerColor = InputBackground,
                    unfocusedContainerColor = InputBackground
                )
            )
        }
    }
}

@Composable
private fun PhotoSection(
    photoPaths: List<String>,
    onAddPhoto: (String) -> Unit,
    onRemovePhoto: (String) -> Unit
) {
    val context = LocalContext.current
    var tempPhotoPath by remember { mutableStateOf<String?>(null) }

    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { success ->
        if (success) {
            tempPhotoPath?.let { onAddPhoto(it) }
        }
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        shape = RoundedCornerShape(14.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("现场拍照 (${photoPaths.size}/5)", color = TextMuted, style = MaterialTheme.typography.bodySmall)
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (photoPaths.size < 5) {
                    Box(
                        modifier = Modifier
                            .size(80.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .border(1.dp, InputBorder, RoundedCornerShape(10.dp))
                            .background(InputBackground)
                            .clickable {
                                val file = File(context.cacheDir, "photo_${System.currentTimeMillis()}.jpg")
                                tempPhotoPath = file.absolutePath
                                val uri = FileProvider.getUriForFile(
                                    context,
                                    "${context.packageName}.fileprovider",
                                    file
                                )
                                cameraLauncher.launch(uri)
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Filled.CameraAlt, "拍照", tint = PrimaryCyan, modifier = Modifier.size(28.dp))
                    }
                }

                photoPaths.forEach { path ->
                    Box(
                        modifier = Modifier
                            .size(80.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .border(1.dp, SuccessGreen.copy(alpha = 0.3f), RoundedCornerShape(10.dp))
                            .background(InputBackground),
                        contentAlignment = Alignment.TopEnd
                    ) {
                        Icon(
                            Icons.Filled.CheckCircle, null,
                            tint = SuccessGreen,
                            modifier = Modifier
                                .padding(4.dp)
                                .size(16.dp)
                        )
                        IconButton(
                            onClick = { onRemovePhoto(path) },
                            modifier = Modifier.align(Alignment.TopEnd).size(20.dp)
                        ) {
                            Icon(Icons.Filled.Close, null, tint = DangerRed, modifier = Modifier.size(14.dp))
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SuccessContent(message: String, onBack: () -> Unit) {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.padding(48.dp)) {
            Box(
                modifier = Modifier
                    .size(100.dp)
                    .clip(CircleShape)
                    .background(SuccessGreen.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Filled.CheckCircle, null, tint = SuccessGreen, modifier = Modifier.size(56.dp))
            }

            Spacer(modifier = Modifier.height(24.dp))
            Text("打卡成功", color = TextPrimary, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            Text(message, color = TextSecondary, style = MaterialTheme.typography.bodyLarge, textAlign = TextAlign.Center)

            Spacer(modifier = Modifier.height(32.dp))
            Button(
                onClick = onBack,
                modifier = Modifier
                    .fillMaxWidth(0.6f)
                    .height(48.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = PrimaryCyan,
                    contentColor = DarkBackground
                )
            ) {
                Text("返回列表", fontWeight = FontWeight.Bold, fontSize = 15.sp)
            }
        }
    }
}
