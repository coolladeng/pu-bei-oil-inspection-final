package com.oilinspection.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.oilinspection.app.ui.home.HomeScreen
import com.oilinspection.app.ui.inspection.InspectionScreen
import com.oilinspection.app.ui.login.LoginScreen
import com.oilinspection.app.ui.login.LoginViewModel
import java.net.URLDecoder
import java.net.URLEncoder

object Routes {
    const val LOGIN = "login"
    const val HOME = "home"
    const val INSPECTION = "inspection/{planId}/{pointId}/{pointName}"

    fun inspection(planId: Long, pointId: Long, pointName: String): String {
        val encoded = URLEncoder.encode(pointName, "UTF-8")
        return "inspection/$planId/$pointId/$encoded"
    }
}

@Composable
fun NavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Routes.LOGIN
    ) {
        composable(Routes.LOGIN) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            )
        }
        composable(Routes.HOME) {
            HomeScreen(
                onNavigateToInspection = { planId, pointId, pointName ->
                    navController.navigate(Routes.inspection(planId, pointId, pointName))
                },
                onLogout = {
                    navController.navigate(Routes.LOGIN) {
                        popUpTo(Routes.HOME) { inclusive = true }
                    }
                }
            )
        }
        composable(
            route = Routes.INSPECTION,
            arguments = listOf(
                navArgument("planId") { type = NavType.LongType },
                navArgument("pointId") { type = NavType.LongType },
                navArgument("pointName") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val planId = backStackEntry.arguments?.getLong("planId") ?: 0L
            val pointId = backStackEntry.arguments?.getLong("pointId") ?: 0L
            val pointName = URLDecoder.decode(
                backStackEntry.arguments?.getString("pointName") ?: "",
                "UTF-8"
            )

            InspectionScreen(
                planId = planId,
                pointId = pointId,
                pointName = pointName,
                onBack = { navController.popBackStack() },
                onCompleted = { navController.popBackStack() }
            )
        }
    }
}
