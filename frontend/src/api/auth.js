import request from '@/utils/request'

export function loginApi(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

export function getCurrentUserApi() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}
