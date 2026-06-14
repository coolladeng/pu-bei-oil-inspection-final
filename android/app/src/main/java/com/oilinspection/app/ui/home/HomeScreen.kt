package com.oilinspection.app.ui.home

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Nfc
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Radar
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.oilinspection.app.data.api.RunPlanItem
import com.oilinspection.app.ui.theme.DangerRed
import com.oilinspection.app.ui.theme.DarkBackground
import com.oilinspection.app.ui.theme.DarkCard
import com.oilinspection.app.ui.theme.DarkSurface
import com.oilinspection.app.ui.theme.DarkSurfaceVariant
import com.oilinspection.app.ui.theme.PrimaryCyan
import com.oilinspection.app.ui.theme.SuccessGreen
import com.oilinspection.app.ui.theme.TextMuted
import com.oilinspection.app.ui.theme.TextPrimary
import com.oilinspection.app.ui.theme.TextSecondary
import com.oilinspection.app.ui.theme.WarningAmber
import com.oilinspection.app.data.api.EquipmentItem
import com.oilinspection.app.data.api.HazardItem
import com.oilinspection.app.data.api.UserProfile

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToInspection: (planId: Long, pointId: Long, pointName: String) -> Unit,
    onLogout: () -> Unit,
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var selectedTab by remember { mutableIntStateOf(0) }

    Scaffold(
        containerColor = DarkBackground,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("巡检管理", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = TextPrimary)
                        Text(
                            "今日巡检 ${uiState.completedCount}/${uiState.totalCount}",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextMuted
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.loadTodayPlans() }) {
                        Icon(Icons.Filled.Refresh, "刷新", tint = TextSecondary)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = DarkSurface,
                    titleContentColor = TextPrimary
                )
            )
        },
        bottomBar = {
            BottomNavBar(
                selectedTab = selectedTab,
                onTabSelected = { selectedTab = it }
            )
        }
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues)) {
            when (selectedTab) {
                0 -> InspectionTabContent(
                    uiState = uiState,
                    onRefresh = viewModel::loadTodayPlans,
                    onItemClick = { plan ->
                        onNavigateToInspection(plan.id, plan.pointId, plan.pointName ?: "")
                    }
                )
                1 -> EquipmentTab(equipments = uiState.equipments, isLoading = uiState.isLoading, onLoad = { viewModel.loadEquipments() })
                2 -> HazardTab(hazards = uiState.hazards, isLoading = uiState.isLoading, onLoad = { viewModel.loadHazards() })
                3 -> ProfileTab(
                    profile = uiState.profile,
                    onLogout = {
                        viewModel.logout()
                        onLogout()
                    },
                    onLoad = { viewModel.loadProfile() }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun InspectionTabContent(
    uiState: HomeUiState,
    onRefresh: () -> Unit,
    onItemClick: (RunPlanItem) -> Unit
) {
    PullToRefreshBox(
        isRefreshing = uiState.isLoading,
        onRefresh = onRefresh,
        modifier = Modifier.fillMaxSize()
    ) {
        if (uiState.errorMessage != null && uiState.todayPlans.isEmpty()) {
            ErrorContent(uiState.errorMessage!!, onRefresh)
        } else if (uiState.todayPlans.isEmpty() && !uiState.isLoading) {
            EmptyContent("今日暂无巡检任务", onRefresh)
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // 进度概览卡片
                item {
                    Spacer(modifier = Modifier.height(4.dp))
                    ProgressCard(
                        completed = uiState.completedCount,
                        total = uiState.totalCount
                    )
                }

                // 同步提示
                item {
                    AnimatedVisibility(visible = uiState.syncedCount > 0) {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = SuccessGreen.copy(alpha = 0.15f)),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(Icons.Filled.CheckCircle, null, tint = SuccessGreen, modifier = Modifier.size(20.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("已同步 ${uiState.syncedCount} 条离线记录", color = SuccessGreen, style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                }

                // 巡检任务列表
                items(uiState.todayPlans, key = { it.id }) { plan ->
                    InspectionPlanCard(
                        plan = plan,
                        onClick = { onItemClick(plan) }
                    )
                }

                item { Spacer(modifier = Modifier.height(16.dp)) }
            }
        }
    }
}

@Composable
private fun ProgressCard(completed: Int, total: Int) {
    val progress = if (total > 0) completed.toFloat() / total else 0f

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("今日进度", style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text(
                    "${(progress * 100).toInt()}%",
                    style = MaterialTheme.typography.titleLarge,
                    color = if (progress == 1f) SuccessGreen else PrimaryCyan,
                    fontWeight = FontWeight.Bold
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp)),
                color = if (progress == 1f) SuccessGreen else PrimaryCyan,
                trackColor = DarkSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("已完成 $completed", color = SuccessGreen, style = MaterialTheme.typography.bodySmall)
                Text("待巡检 ${total - completed}", color = WarningAmber, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
private fun InspectionPlanCard(plan: RunPlanItem, onClick: () -> Unit) {
    val isCompleted = plan.status == 1
    val cardColor = if (isCompleted) DarkCard.copy(alpha = 0.5f) else DarkCard

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = !isCompleted) { onClick() },
        colors = CardDefaults.cardColors(containerColor = cardColor),
        shape = RoundedCornerShape(14.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 状态图标
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(CircleShape)
                    .background(
                        if (isCompleted) SuccessGreen.copy(alpha = 0.15f)
                        else PrimaryCyan.copy(alpha = 0.15f)
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = if (isCompleted) Icons.Filled.CheckCircle else Icons.Filled.Nfc,
                    contentDescription = null,
                    tint = if (isCompleted) SuccessGreen else PrimaryCyan,
                    modifier = Modifier.size(24.dp)
                )
            }

            Spacer(modifier = Modifier.width(14.dp))

            // 信息区
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = plan.pointName ?: "巡检点 #${plan.pointId}",
                    style = MaterialTheme.typography.titleMedium,
                    color = if (isCompleted) TextMuted else TextPrimary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Filled.LocationOn, null,
                        tint = TextMuted, modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = plan.deptName ?: "",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextMuted
                    )
                }
            }

            // 状态标签
            Text(
                text = if (isCompleted) "已检" else "待检",
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
                color = if (isCompleted) SuccessGreen else PrimaryCyan,
                modifier = Modifier
                    .clip(RoundedCornerShape(8.dp))
                    .background(
                        if (isCompleted) SuccessGreen.copy(alpha = 0.1f)
                        else PrimaryCyan.copy(alpha = 0.1f)
                    )
                    .padding(horizontal = 12.dp, vertical = 6.dp)
            )

            if (!isCompleted) {
                Spacer(modifier = Modifier.width(8.dp))
                Icon(
                    Icons.Filled.ChevronRight, null,
                    tint = TextMuted,
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}

@Composable
private fun BottomNavBar(selectedTab: Int, onTabSelected: (Int) -> Unit) {
    NavigationBar(
        containerColor = DarkSurface,
        contentColor = PrimaryCyan,
        tonalElevation = 0.dp
    ) {
        BottomNavItem(0, "巡检", Icons.Filled.Radar, selectedTab, onTabSelected)
        BottomNavItem(1, "设备", Icons.Filled.Build, selectedTab, onTabSelected)
        BottomNavItem(2, "隐患", Icons.Filled.Warning, selectedTab, onTabSelected)
        BottomNavItem(3, "我的", Icons.Filled.Person, selectedTab, onTabSelected)
    }
}

@Composable
private fun BottomNavItem(
    index: Int, label: String, icon: ImageVector,
    selectedTab: Int, onTabSelected: (Int) -> Unit
) {
    NavigationBarItem(
        selected = selectedTab == index,
        onClick = { onTabSelected(index) },
        icon = { Icon(icon, label, modifier = Modifier.size(24.dp)) },
        label = { Text(label, fontSize = 11.sp) },
        colors = NavigationBarItemDefaults.colors(
            selectedIconColor = PrimaryCyan,
            selectedTextColor = PrimaryCyan,
            unselectedIconColor = TextMuted,
            unselectedTextColor = TextMuted,
            indicatorColor = PrimaryCyan.copy(alpha = 0.1f)
        )
    )
}


@Composable
private fun EquipmentTab(
    equipments: List<EquipmentItem>,
    isLoading: Boolean,
    onLoad: () -> Unit
) {
    LaunchedEffect(Unit) { onLoad() }

    PullToRefreshBox(
        isRefreshing = isLoading,
        onRefresh = onLoad,
        modifier = Modifier.fillMaxSize()
    ) {
        if (equipments.isEmpty() && !isLoading) {
            EmptyContent("暂无设备数据") { onLoad() }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(10.dp),
                contentPadding = PaddingValues(16.dp)
            ) {
                items(equipments) { equip ->
                    EquipmentCard(equip)
                }
            }
        }
    }
}

@Composable
private fun EquipmentCard(equip: EquipmentItem) {
    val statusLabel = when (equip.status) {
        1 -> "正常"
        2 -> "维修中"
        3 -> "报废"
        else -> "未知"
    }
    val statusColor = when (equip.status) {
        1 -> SuccessGreen
        2 -> WarningAmber
        3 -> DangerRed
        else -> TextMuted
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(PrimaryCyan.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Filled.Build, null, tint = PrimaryCyan, modifier = Modifier.size(22.dp))
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(equip.name, color = TextPrimary, fontWeight = FontWeight.Medium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Spacer(modifier = Modifier.height(2.dp))
                Row {
                    equip.modelNo?.let {
                        Text(it, color = TextMuted, style = MaterialTheme.typography.bodySmall)
                        Spacer(modifier = Modifier.width(8.dp))
                    }
                    equip.deptName?.let { Text(it, color = TextMuted, style = MaterialTheme.typography.bodySmall) }
                }
            }
            Text(
                statusLabel, color = statusColor,
                style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold,
                modifier = Modifier
                    .clip(RoundedCornerShape(8.dp))
                    .background(statusColor.copy(alpha = 0.1f))
                    .padding(horizontal = 10.dp, vertical = 4.dp)
            )
        }
    }
}

@Composable
private fun HazardTab(
    hazards: List<HazardItem>,
    isLoading: Boolean,
    onLoad: () -> Unit
) {
    LaunchedEffect(Unit) { onLoad() }

    PullToRefreshBox(
        isRefreshing = isLoading,
        onRefresh = onLoad,
        modifier = Modifier.fillMaxSize()
    ) {
        if (hazards.isEmpty() && !isLoading) {
            EmptyContent("暂无隐患记录") { onLoad() }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(10.dp),
                contentPadding = PaddingValues(16.dp)
            ) {
                items(hazards) { hazard ->
                    HazardCard(hazard)
                }
            }
        }
    }
}

@Composable
private fun HazardCard(hazard: HazardItem) {
    val urgencyLabel = when (hazard.urgency) {
        "urgent" -> "紧急"
        "important" -> "重要"
        else -> "一般"
    }
    val urgencyColor = when (hazard.urgency) {
        "urgent" -> DangerRed
        "important" -> WarningAmber
        else -> TextMuted
    }
    val statusLabel = when (hazard.status) {
        "reported" -> "已上报"
        "reviewing" -> "审核中"
        "handling" -> "处理中"
        "completed" -> "已完成"
        "closed" -> "已关闭"
        else -> hazard.status
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(hazard.title, color = TextPrimary, fontWeight = FontWeight.Medium,
                    modifier = Modifier.weight(1f), maxLines = 2, overflow = TextOverflow.Ellipsis)
                Spacer(modifier = Modifier.width(8.dp))
                Text(urgencyLabel, color = urgencyColor, fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.labelMedium,
                    modifier = Modifier
                        .clip(RoundedCornerShape(6.dp))
                        .background(urgencyColor.copy(alpha = 0.1f))
                        .padding(horizontal = 8.dp, vertical = 3.dp))
            }
            Spacer(modifier = Modifier.height(8.dp))
            Row {
                hazard.pointName?.let { TagChip(it) }
                hazard.equipName?.let { TagChip(it) }
                TagChip(statusLabel)
            }
        }
    }
}

@Composable
private fun TagChip(text: String) {
    Text(text, color = TextMuted, style = MaterialTheme.typography.bodySmall,
        modifier = Modifier
            .padding(end = 8.dp)
            .clip(RoundedCornerShape(4.dp))
            .background(TextMuted.copy(alpha = 0.1f))
            .padding(horizontal = 6.dp, vertical = 2.dp))
}

@Composable
private fun ProfileTab(
    profile: UserProfile?,
    onLogout: () -> Unit,
    onLoad: () -> Unit
) {
    LaunchedEffect(Unit) { onLoad() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(32.dp))

        // Avatar
        Box(
            modifier = Modifier
                .size(80.dp)
                .clip(CircleShape)
                .background(PrimaryCyan.copy(alpha = 0.15f)),
            contentAlignment = Alignment.Center
        ) {
            Icon(Icons.Filled.Person, null, tint = PrimaryCyan, modifier = Modifier.size(40.dp))
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            profile?.realName ?: "未登录",
            color = TextPrimary,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(4.dp))

        Text(
            profile?.let { "@" + it.username } ?: "",
            color = TextMuted,
            style = MaterialTheme.typography.bodyMedium
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Info cards
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = DarkCard),
            shape = RoundedCornerShape(14.dp)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                InfoRow("用户名", profile?.username ?: "-")
                HorizontalDivider(color = Color(0xFF1A3355), modifier = Modifier.padding(vertical = 12.dp))
                InfoRow("角色", profile?.roles?.joinToString(", ") ?: "-")
                HorizontalDivider(color = Color(0xFF1A3355), modifier = Modifier.padding(vertical = 12.dp))
                InfoRow("版本", "v1.0.0")
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        // Logout button
        Button(
            onClick = onLogout,
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = DangerRed.copy(alpha = 0.1f),
                contentColor = DangerRed
            )
        ) {
            Text("退出登录", fontWeight = FontWeight.Bold)
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, color = TextMuted, style = MaterialTheme.typography.bodyMedium)
        Text(value, color = TextPrimary, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun ErrorContent(message: String, onRetry: () -> Unit) {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.padding(32.dp)) {
            Icon(Icons.Filled.Warning, null, tint = DangerRed, modifier = Modifier.size(48.dp))
            Spacer(modifier = Modifier.height(16.dp))
            Text(message, color = TextSecondary, style = MaterialTheme.typography.bodyLarge)
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
private fun EmptyContent(message: String, onRefresh: () -> Unit) {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.padding(32.dp)) {
            Icon(Icons.Filled.CheckCircle, null, tint = SuccessGreen.copy(alpha = 0.5f), modifier = Modifier.size(64.dp))
            Spacer(modifier = Modifier.height(16.dp))
            Text(message, color = TextMuted, style = MaterialTheme.typography.bodyLarge)
        }
    }
}
