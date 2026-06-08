<template>
  <div class="page-container">
    <n-card :bordered="false" class="detail-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <n-button @click="goBack" style="margin-right: 12px">
              <template #icon><n-icon><ArrowBack /></n-icon></template>
              返回
            </n-button>
            <span>贷款申请详情</span>
          </div>
          <div class="header-right">
            <n-space v-if="loan && (loan.status === 'manual_review' || loan.status === 'pending')">
              <n-button type="primary" @click="showApproveDialog('approve')">
                <template #icon><n-icon><Checkmark /></n-icon></template>
                通过
              </n-button>
              <n-button type="error" @click="showApproveDialog('reject')">
                <template #icon><n-icon><Close /></n-icon></template>
                拒绝
              </n-button>
            </n-space>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <n-spin size="large" />
      </div>

      <div v-else-if="loan">
        <n-tabs v-model:value="activeTab" type="line">
          <n-tab-pane name="info" tab="基本信息">
            <n-descriptions :columns="2" bordered title="贷款信息">
              <n-descriptions-item label="申请编号">
                {{ loan.id }}
              </n-descriptions-item>
              <n-descriptions-item label="客户姓名">
                {{ loan.customer_name }}
              </n-descriptions-item>
              <n-descriptions-item label="贷款类型">
                {{ getLoanTypeText(loan.loan_type) }}
              </n-descriptions-item>
              <n-descriptions-item label="贷款金额">
                ¥{{ formatMoney(loan.amount) }}
              </n-descriptions-item>
              <n-descriptions-item label="贷款期限">
                {{ loan.term_months }} 个月
              </n-descriptions-item>
              <n-descriptions-item label="贷款利率">
                {{ loan.interest_rate }} %
              </n-descriptions-item>
              <n-descriptions-item label="贷款用途" :span="2">
                {{ loan.purpose }}
              </n-descriptions-item>
              <n-descriptions-item label="月供">
                ¥{{ formatMoney(loan.monthly_payment) }}
              </n-descriptions-item>
              <n-descriptions-item label="风险评分">
                <n-statistic :value="loan.risk_score || 0" />
              </n-descriptions-item>
              <n-descriptions-item label="风险等级">
                {{ riskLevelTag(loan.risk_level) }}
              </n-descriptions-item>
              <n-descriptions-item label="状态">
                {{ applicationStatusTag(loan.status) }}
              </n-descriptions-item>
              <n-descriptions-item label="申请时间">
                {{ formatDate(loan.created_at, 'YYYY-MM-DD HH:mm:ss') }}
              </n-descriptions-item>
              <n-descriptions-item label="审批时间">
                {{ formatDate(loan.approved_at, 'YYYY-MM-DD HH:mm:ss') }}
              </n-descriptions-item>
            </n-descriptions>

            <n-descriptions :columns="2" bordered title="客户信息摘要" style="margin-top: 20px">
              <n-descriptions-item label="姓名">
                {{ loan.customer?.name || '-' }}
              </n-descriptions-item>
              <n-descriptions-item label="身份证号">
                {{ maskIdCard(loan.customer?.id_card) || '-' }}
              </n-descriptions-item>
              <n-descriptions-item label="手机号">
                {{ maskPhone(loan.customer?.phone) || '-' }}
              </n-descriptions-item>
              <n-descriptions-item label="月收入">
                ¥{{ formatMoney(loan.customer?.monthly_income) }}
              </n-descriptions-item>
              <n-descriptions-item label="工作年限" :span="2">
                {{ loan.customer?.work_years }} 年
              </n-descriptions-item>
            </n-descriptions>
          </n-tab-pane>

          <n-tab-pane name="risk" tab="风险评估">
            <div v-if="!loan.risk_assessment" class="empty-state">
              <n-empty description="暂无风险评估数据" />
            </div>
            <div v-else>
              <n-card class="risk-summary-card">
                <n-grid :cols="3" :x-gap="24">
                  <n-grid-item>
                    <div class="stat-item">
                      <div class="stat-label">总评分</div>
                      <div class="stat-value">
                        <n-statistic :value="loan.risk_assessment.total_score || 0" />
                      </div>
                    </div>
                  </n-grid-item>
                  <n-grid-item>
                    <div class="stat-item">
                      <div class="stat-label">风险等级</div>
                      <div class="stat-value">
                        {{ riskLevelTag(loan.risk_assessment.risk_level) }}
                      </div>
                    </div>
                  </n-grid-item>
                  <n-grid-item>
                    <div class="stat-item">
                      <div class="stat-label">评估时间</div>
                      <div class="stat-value text">
                        {{ formatDate(loan.risk_assessment.assessed_at, 'YYYY-MM-DD HH:mm:ss') }}
                      </div>
                    </div>
                  </n-grid-item>
                </n-grid>
                <n-divider />
                <div class="score-description">
                  <div class="description-label">评分说明</div>
                  <div class="description-content">
                    {{ loan.risk_assessment.description || '暂无评分说明' }}
                  </div>
                </div>
              </n-card>

              <n-card title="评分明细" :bordered="false" style="margin-top: 20px">
                <n-data-table
                  :columns="scoreDetailColumns"
                  :data="loan.risk_assessment.score_details || []"
                  :pagination="false"
                />
              </n-card>

              <n-card title="触发风控规则" :bordered="false" style="margin-top: 20px">
                <div v-if="!loan.risk_assessment.triggered_rules || loan.risk_assessment.triggered_rules.length === 0" class="empty-state">
                  <n-empty description="未触发风控规则" />
                </div>
                <n-timeline v-else>
                  <n-timeline-item
                    v-for="(rule, index) in loan.risk_assessment.triggered_rules"
                    :key="index"
                    :type="rule.severity === 'high' ? 'error' : rule.severity === 'medium' ? 'warning' : 'default'"
                    :title="rule.rule_name"
                  >
                    <n-card size="small" class="rule-card">
                      <n-descriptions :columns="2" size="small">
                        <n-descriptions-item label="规则编码">
                          {{ rule.rule_code }}
                        </n-descriptions-item>
                        <n-descriptions-item label="严重程度">
                          <n-tag :type="rule.severity === 'high' ? 'error' : rule.severity === 'medium' ? 'warning' : 'default'">
                            {{ rule.severity === 'high' ? '高' : rule.severity === 'medium' ? '中' : '低' }}
                          </n-tag>
                        </n-descriptions-item>
                        <n-descriptions-item label="规则描述" :span="2">
                          {{ rule.description }}
                        </n-descriptions-item>
                        <n-descriptions-item label="触发条件" :span="2">
                          {{ rule.trigger_condition }}
                        </n-descriptions-item>
                      </n-descriptions>
                    </n-card>
                  </n-timeline-item>
                </n-timeline>
              </n-card>
            </div>
          </n-tab-pane>

          <n-tab-pane name="approval" tab="审批记录">
            <div v-if="approvalRecords.length === 0" class="empty-state">
              <n-empty description="暂无审批记录" />
            </div>
            <n-timeline v-else>
              <n-timeline-item
                v-for="record in approvalRecords"
                :key="record.id"
                :type="getApprovalType(record.action)"
                :title="record.operator_name || '系统'"
                :time="formatDate(record.created_at, 'YYYY-MM-DD HH:mm:ss')"
              >
                <n-card size="small" class="approval-card">
                  <n-descriptions :columns="2" size="small">
                    <n-descriptions-item label="操作类型">
                      <n-tag :type="getApprovalType(record.action)">
                        {{ getApprovalActionText(record.action) }}
                      </n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item label="操作人">
                      {{ record.operator_name || '系统自动' }}
                    </n-descriptions-item>
                    <n-descriptions-item label="审批意见" :span="2">
                      {{ record.comments || '无' }}
                    </n-descriptions-item>
                  </n-descriptions>
                </n-card>
              </n-timeline-item>
            </n-timeline>
          </n-tab-pane>
        </n-tabs>
      </div>
    </n-card>

    <n-modal v-model:show="showApproveModal" preset="card" :title="approveModalTitle" :style="{ width: '500px' }">
      <n-form
        ref="approveFormRef"
        :model="approveFormData"
        :rules="approveFormRules"
        label-placement="left"
        label-width="100px"
      >
        <n-form-item label="审批意见" path="comments">
          <n-input
            v-model:value="approveFormData.comments"
            type="textarea"
            placeholder="请输入审批意见"
            :rows="4"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showApproveModal = false">取消</n-button>
          <n-button
            :type="currentAction === 'approve' ? 'primary' : 'error'"
            :loading="submitLoading"
            @click="handleApproval"
          >
            {{ currentAction === 'approve' ? '通过' : '拒绝' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { ArrowBack, Checkmark, Close } from '@vicons/ionicons5'
import { getLoanApplicationDetail, approveLoanApplication, rejectLoanApplication, getApprovalRecords } from '@/api/loan'
import { riskLevelTag, applicationStatusTag, formatDate, formatMoney, getLoanTypeText, maskIdCard, maskPhone } from '@/utils'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const submitLoading = ref(false)
const activeTab = ref('info')
const loan = ref(null)
const approvalRecords = ref([])

const showApproveModal = ref(false)
const approveFormRef = ref(null)
const currentAction = ref(null)

const loanId = route.params.id

const approveFormData = reactive({
  comments: ''
})

const approveFormRules = {
  comments: { required: true, message: '请输入审批意见', trigger: 'blur' }
}

const scoreDetailColumns = [
  { title: '评分维度', key: 'dimension', width: 150 },
  { title: '得分', key: 'score', width: 100 },
  { title: '权重', key: 'weight', width: 100, render: (row) => `${(row.weight * 100).toFixed(0)}%` },
  { title: '说明', key: 'description' }
]

const approveModalTitle = computed(() => {
  return currentAction.value === 'approve' ? '通过贷款申请' : '拒绝贷款申请'
})

function getApprovalType(action) {
  const typeMap = {
    approve: 'success',
    reject: 'error',
    auto_approve: 'success',
    auto_reject: 'error'
  }
  return typeMap[action] || 'default'
}

function getApprovalActionText(action) {
  const textMap = {
    approve: '通过',
    reject: '拒绝',
    auto_approve: '自动通过',
    auto_reject: '自动拒绝'
  }
  return textMap[action] || action
}

async function fetchData() {
  loading.value = true
  try {
    const [loanRes, recordsRes] = await Promise.all([
      getLoanApplicationDetail(loanId),
      getApprovalRecords(loanId)
    ])
    loan.value = loanRes.data
    approvalRecords.value = recordsRes.data.items || recordsRes.data || []
  } catch (error) {
    console.error('Failed to fetch loan detail:', error)
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

function showApproveDialog(action) {
  currentAction.value = action
  approveFormData.comments = ''
  showApproveModal.value = true
}

async function handleApproval() {
  try {
    await approveFormRef.value?.validate()
    submitLoading.value = true
    if (currentAction.value === 'approve') {
      await approveLoanApplication(loanId, {
        comments: approveFormData.comments
      })
      message.success('审批通过成功')
    } else {
      await rejectLoanApplication(loanId, {
        comments: approveFormData.comments
      })
      message.success('审批拒绝成功')
    }
    showApproveModal.value = false
    fetchData()
  } catch (error) {
    console.error('Approval failed:', error)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.detail-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;

  .header-left {
    display: flex;
    align-items: center;
  }
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.risk-summary-card {
  border-radius: 8px;

  .stat-item {
    text-align: center;

    .stat-label {
      font-size: 13px;
      color: #999;
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 20px;
      font-weight: 600;

      &.text {
        font-size: 14px;
        font-weight: normal;
        color: #333;
      }
    }
  }

  .score-description {
    .description-label {
      font-size: 13px;
      color: #999;
      margin-bottom: 8px;
    }

    .description-content {
      font-size: 14px;
      color: #333;
      line-height: 1.6;
    }
  }
}

.rule-card {
  margin-top: 8px;
}

.approval-card {
  margin-top: 8px;
}
</style>
