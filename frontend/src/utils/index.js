import { h } from 'vue'
import { NTag } from 'naive-ui'
import dayjs from 'dayjs'

export function riskLevelTag(level) {
  const tagMap = {
    low: { type: 'success', text: '低风险' },
    medium_low: { type: 'success', text: '中低风险' },
    medium: { type: 'warning', text: '中风险' },
    medium_high: { type: 'warning', text: '中高风险' },
    high: { type: 'error', text: '高风险' },
    extreme_high: { type: 'error', text: '极高风险' }
  }
  const config = tagMap[level] || { type: 'default', text: '未评估' }
  return h(NTag, { type: config.type, size: 'small' }, { default: () => config.text })
}

export function applicationStatusTag(status) {
  const tagMap = {
    pending: { type: 'default', text: '待审核' },
    auto_approved: { type: 'success', text: '自动通过' },
    auto_rejected: { type: 'error', text: '自动拒绝' },
    manual_review: { type: 'warning', text: '人工审核' },
    approved: { type: 'success', text: '已通过' },
    rejected: { type: 'error', text: '已拒绝' }
  }
  const config = tagMap[status] || { type: 'default', text: status }
  return h(NTag, { type: config.type, size: 'small' }, { default: () => config.text })
}

export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

export function formatMoney(amount, decimals = 2) {
  if (amount === null || amount === undefined || isNaN(amount)) return '-'
  return Number(amount).toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

export function getRiskLevelTag(level) {
  const map = {
    low: { class: 'risk-tag-low', text: '低风险' },
    medium_low: { class: 'risk-tag-medium-low', text: '中低风险' },
    medium: { class: 'risk-tag-medium', text: '中风险' },
    medium_high: { class: 'risk-tag-medium-high', text: '中高风险' },
    high: { class: 'risk-tag-high', text: '高风险' },
    extreme_high: { class: 'risk-tag-extreme-high', text: '极高风险' }
  }
  return map[level] || { class: 'risk-tag-medium', text: '未评估' }
}

export function getLoanStatusText(status) {
  const map = {
    pending: '待提交',
    reviewing: '审核中',
    auto_approved: '自动通过',
    auto_rejected: '自动拒绝',
    manual_review: '人工审核',
    approved: '已通过',
    rejected: '已拒绝',
    cancelled: '已取消'
  }
  return map[status] || status
}

export function getLoanStatusType(status) {
  const map = {
    pending: 'default',
    reviewing: 'warning',
    auto_approved: 'success',
    auto_rejected: 'error',
    manual_review: 'warning',
    approved: 'success',
    rejected: 'error',
    cancelled: 'default'
  }
  return map[status] || 'default'
}

export function getLoanTypeText(type) {
  const map = {
    personal: '个人贷款',
    business: '企业贷款',
    mortgage: '抵押贷款',
    car: '车贷',
    consumer: '消费贷款'
  }
  return map[type] || type
}

export function getRoleText(role) {
  const map = {
    admin: '系统管理员',
    manager: '部门经理',
    reviewer: '审核员',
    operator: '操作员'
  }
  return map[role] || role
}

export function getBlacklistTypeText(type) {
  const map = {
    fraud: '欺诈',
    overdue: '逾期',
    bad_credit: '不良信用',
    other: '其他'
  }
  return map[type] || type
}

export function maskIdCard(idCard) {
  if (!idCard || idCard.length < 8) return idCard
  return idCard.substring(0, 6) + '********' + idCard.substring(14)
}

export function maskPhone(phone) {
  if (!phone || phone.length < 11) return phone
  return phone.substring(0, 3) + '****' + phone.substring(7)
}

export function validateIdCard(idCard) {
  const reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
  return reg.test(idCard)
}

export function validatePhone(phone) {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(phone)
}
