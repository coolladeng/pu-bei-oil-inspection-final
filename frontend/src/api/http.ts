import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器 - 自动附加 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 - 统一错误处理
request.interceptors.response.use(
  (response) => {
    // 直接返回后端数据（后端直接返回原始数据，无 code/message/data 包装）
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else if (error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED') {
      // 真正的网络错误（服务器不可达或超时）
      ElMessage.error('服务器连接失败，请检查后端服务是否启动')
    } else if (error.response) {
      // 服务器返回了错误响应
      const msg = error.response.data?.detail || error.response.data?.message || error.response.statusText || '服务器错误'
      ElMessage.error(msg)
    } else {
      ElMessage.error('请求失败，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default request