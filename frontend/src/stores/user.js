import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, getCurrentUserApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isManager = computed(() => userInfo.value?.role === 'admin' || userInfo.value?.role === 'manager')

  async function login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const res = await loginApi(formData)
    token.value = res.data.access_token
    userInfo.value = res.data.user
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res.data
  }

  async function fetchCurrentUser() {
    try {
      const res = await getCurrentUserApi()
      userInfo.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
      return res.data
    } catch (error) {
      logout()
      throw error
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    isManager,
    login,
    fetchCurrentUser,
    logout
  }
})
