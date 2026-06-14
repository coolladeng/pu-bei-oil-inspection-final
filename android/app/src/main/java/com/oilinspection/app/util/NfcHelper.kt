package com.oilinspection.app.util

import android.app.Activity
import android.app.PendingIntent
import android.content.Intent
import android.content.IntentFilter
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.NfcA
import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NfcHelper @Inject constructor() {

    companion object {
        private const val TAG = "NfcHelper"
    }

    /**
     * 检查设备是否支持 NFC
     */
    fun isNfcSupported(adapter: NfcAdapter?): Boolean {
        return adapter != null
    }

    /**
     * 检查 NFC 是否已开启
     */
    fun isNfcEnabled(adapter: NfcAdapter?): Boolean {
        return adapter?.isEnabled == true
    }

    /**
     * 启用前台 NFC 分发 (activity 在前台时优先处理 NFC 标签)
     */
    fun enableForegroundDispatch(activity: Activity, adapter: NfcAdapter?) {
        if (adapter == null) return
        val intent = PendingIntent.getActivity(
            activity, 0,
            Intent(activity, activity.javaClass).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val filters = arrayOf(IntentFilter(NfcAdapter.ACTION_TECH_DISCOVERED))
        val techList = arrayOf(arrayOf(NfcA::class.java.name, NfcA::class.java.name))

        try {
            adapter.enableForegroundDispatch(activity, intent, filters, techList)
        } catch (e: Exception) {
            Log.e(TAG, "启用前台NFC分发失败: ${e.message}")
        }
    }

    /**
     * 禁用前台 NFC 分发
     */
    fun disableForegroundDispatch(activity: Activity, adapter: NfcAdapter?) {
        try {
            adapter?.disableForegroundDispatch(activity)
        } catch (e: Exception) {
            Log.e(TAG, "禁用前台NFC分发失败: ${e.message}")
        }
    }

    /**
     * 从 Intent 中读取 NFC 标签 UID
     * NfcA 标签 UID 为 7 字节
     */
    fun readUidFromIntent(intent: Intent?): String? {
        val tag: Tag? = intent?.getParcelableExtra(NfcAdapter.EXTRA_TAG)
        return tag?.id?.let { bytesToHex(it) }
    }

    /**
     * 字节数组转十六进制字符串 (大写，无分隔符)
     */
    fun bytesToHex(bytes: ByteArray): String {
        return bytes.joinToString("") { "%02X".format(it) }
    }
}
