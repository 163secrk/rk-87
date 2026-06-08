import request from '@/utils/request'

export function getLoanList(params) {
  return request({
    url: '/loan-applications',
    method: 'get',
    params
  })
}

export function getLoanApplicationList(params) {
  return getLoanList(params)
}

export function getLoanDetail(id) {
  return request({
    url: `/loan-applications/${id}`,
    method: 'get'
  })
}

export function getLoanApplicationDetail(id) {
  return getLoanDetail(id)
}

export function createLoan(data) {
  return request({
    url: '/loan-applications',
    method: 'post',
    data
  })
}

export function createLoanApplication(data) {
  return createLoan(data)
}

export function updateLoan(id, data) {
  return request({
    url: `/loan-applications/${id}`,
    method: 'put',
    data
  })
}

export function assessLoan(id) {
  return request({
    url: `/loan-applications/${id}/assess`,
    method: 'post'
  })
}

export function reviewLoan(id, action, comment) {
  return request({
    url: `/loan-applications/${id}/review`,
    method: 'post',
    params: { action, comment }
  })
}

export function approveLoanApplication(id, data) {
  return request({
    url: `/loan-applications/${id}/approve`,
    method: 'post',
    data
  })
}

export function rejectLoanApplication(id, data) {
  return request({
    url: `/loan-applications/${id}/reject`,
    method: 'post',
    data
  })
}

export function getCustomerLoanList(customerId) {
  return request({
    url: `/customers/${customerId}/loan-applications`,
    method: 'get'
  })
}

export function getApprovalRecords(id) {
  return request({
    url: `/loan-applications/${id}/approval-records`,
    method: 'get'
  })
}
