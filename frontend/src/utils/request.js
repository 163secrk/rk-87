import axios from 'axios'
import router from '@/router'

let messageInstance = null

export function setMessageInstance(instance) {
  messageInstance = instance
}

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000
})

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 200) {
      return res
    } else {
      if (messageInstance) {
        messageInstance.error(res.message || '请求失败')
      }
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  (error) => {
    if (messageInstance) {
      if (error.response) {
        if (error.response.status === 401) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.push('/login')
          messageInstance.error('登录已过期，请重新登录')
        } else if (error.response.status === 403) {
          messageInstance.error('没有权限访问该资源')
        } else if (error.response.status === 404) {
          messageInstance.error('请求的资源不存在')
        } else if (error.response.status === 500) {
          messageInstance.error('服务器内部错误')
        } else {
          messageInstance.error(error.response.data?.message || '请求失败')
        }
      } else if (error.request) {
        messageInstance.error('网络错误，请检查网络连接')
      } else {
        messageInstance.error('请求失败')
      }
    }
    return Promise.reject(error)
  }
)

export default request
