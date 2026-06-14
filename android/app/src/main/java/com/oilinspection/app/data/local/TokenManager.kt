package com.oilinspection.app.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    companion object {
        private val KEY_ACCESS_TOKEN = stringPreferencesKey("access_token")
        private val KEY_USER_NAME = stringPreferencesKey("user_name")
        private val KEY_REAL_NAME = stringPreferencesKey("real_name")
        private val KEY_ROLE = stringPreferencesKey("role")
    }

    val accessToken: Flow<String?>
        get() = context.dataStore.data.map { it[KEY_ACCESS_TOKEN] }

    val realName: Flow<String?>
        get() = context.dataStore.data.map { it[KEY_REAL_NAME] }

    suspend fun getToken(): String? {
        return context.dataStore.data.first()[KEY_ACCESS_TOKEN]
    }

    suspend fun saveLoginInfo(
        token: String,
        username: String,
        realName: String,
        role: String
    ) {
        context.dataStore.edit {
            it[KEY_ACCESS_TOKEN] = token
            it[KEY_USER_NAME] = username
            it[KEY_REAL_NAME] = realName
            it[KEY_ROLE] = role
        }
    }

    suspend fun clear() {
        context.dataStore.edit { it.clear() }
    }
}
