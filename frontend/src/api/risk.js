import request from '@/utils/request'

export function getRiskRuleList(params) {
  return request({
    url: '/risk-rules',
    method: 'get',
    params
  })
}

export function getAllRiskRules() {
  return request({
    url: '/risk-rules/all',
    method: 'get'
  })
}

export function getRiskRuleDetail(id) {
  return request({
    url: `/risk-rules/${id}`,
    method: 'get'
  })
}

export function createRiskRule(data) {
  return request({
    url: '/risk-rules',
    method: 'post',
    data
  })
}

export function updateRiskRule(id, data) {
  return request({
    url: `/risk-rules/${id}`,
    method: 'put',
    data
  })
}

export function deleteRiskRule(id) {
  return request({
    url: `/risk-rules/${id}`,
    method: 'delete'
  })
}

export function toggleRiskRule(id) {
  return request({
    url: `/risk-rules/${id}/toggle`,
    method: 'post'
  })
}

export function getBlacklist(params) {
  return request({
    url: '/blacklist',
    method: 'get',
    params
  })
}

export function checkBlacklist(idCard) {
  return request({
    url: `/blacklist/check/${idCard}`,
    method: 'get'
  })
}

export function getBlacklistDetail(id) {
  return request({
    url: `/blacklist/${id}`,
    method: 'get'
  })
}

export function addBlacklist(data) {
  return request({
    url: '/blacklist',
    method: 'post',
    data
  })
}

export function updateBlacklist(id, data) {
  return request({
    url: `/blacklist/${id}`,
    method: 'put',
    data
  })
}

export function removeBlacklist(id, reason) {
  return request({
    url: `/blacklist/${id}/remove`,
    method: 'post',
    params: { reason }
  })
}

export function addToBlacklist(data) {
  return addBlacklist(data)
}

export function removeFromBlacklist(id) {
  return removeBlacklist(id, '手动移除')
}

export function getCreditReportList(params) {
  return request({
    url: '/credit-reports',
    method: 'get',
    params
  })
}

export function getCreditReportDetail(id) {
  return request({
    url: `/credit-reports/${id}`,
    method: 'get'
  })
}

export function createCreditReport(data) {
  return request({
    url: '/credit-reports',
    method: 'post',
    data
  })
}

export function queryCreditReport(customerId, reportSource) {
  return request({
    url: `/credit-reports/query/${customerId}`,
    method: 'post',
    params: { report_source: reportSource }
  })
}

export function getDashboardStats() {
  return request({
    url: '/dashboard/stats',
    method: 'get'
  })
}

export function getTrendData(days) {
  return request({
    url: '/dashboard/trend',
    method: 'get',
    params: { days }
  })
}

export function getLoanTypeDistribution() {
  return request({
    url: '/dashboard/loan-type-distribution',
    method: 'get'
  })
}
