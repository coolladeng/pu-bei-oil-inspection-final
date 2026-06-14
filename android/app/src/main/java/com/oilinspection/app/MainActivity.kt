package com.oilinspection.app

import android.content.Intent
import android.nfc.NfcAdapter
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.navigation.compose.rememberNavController
import com.oilinspection.app.ui.inspection.InspectionViewModel
import com.oilinspection.app.ui.navigation.NavGraph
import com.oilinspection.app.ui.theme.OilInspectionTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            OilInspectionTheme {
                val navController = rememberNavController()
                NavGraph(navController = navController)
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
    }

    override fun onPause() {
        super.onPause()
        val nfcAdapter = NfcAdapter.getDefaultAdapter(this)
        nfcAdapter?.disableForegroundDispatch(this)
    }

    override fun onResume() {
        super.onResume()
        val nfcAdapter = NfcAdapter.getDefaultAdapter(this)
        val intent = android.app.PendingIntent.getActivity(
            this, 0,
            Intent(this, javaClass).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
            android.app.PendingIntent.FLAG_IMMUTABLE or android.app.PendingIntent.FLAG_UPDATE_CURRENT
        )
        val filters = arrayOf(android.content.IntentFilter(NfcAdapter.ACTION_TECH_DISCOVERED))
        val techList = arrayOf(
            arrayOf(android.nfc.tech.NfcA::class.java.name, android.nfc.tech.NfcA::class.java.name)
        )
        try {
            nfcAdapter?.enableForegroundDispatch(this, intent, filters, techList)
        } catch (_: Exception) {}
    }
}
