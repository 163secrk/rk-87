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
            <span>客户详情</span>
          </div>
          <div class="header-right">
            <n-space>
              <n-button type="primary" @click="showAddLoanModal">
                <template #icon><n-icon><Add /></n-icon></template>
                新增贷款申请
              </n-button>
            </n-space>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <n-spin size="large" />
      </div>

      <div v-else-if="customer">
        <n-tabs v-model:value="activeTab" type="line">
          <n-tab-pane name="info" tab="基本信息">
            <n-descriptions :columns="2" bordered>
              <n-descriptions-item label="客户姓名">
                {{ customer.name }}
              </n-descriptions-item>
              <n-descriptions-item label="性别">
                {{ customer.gender === 'male' ? '男' : '女' }}
              </n-descriptions-item>
              <n-descriptions-item label="身份证号">
                {{ customer.id_card }}
              </n-descriptions-item>
              <n-descriptions-item label="手机号">
                {{ customer.phone }}
              </n-descriptions-item>
              <n-descriptions-item label="年龄">
                {{ customer.age }} 岁
              </n-descriptions-item>
              <n-descriptions-item label="学历">
                {{ educationMap[customer.education] || customer.education }}
              </n-descriptions-item>
              <n-descriptions-item label="婚姻状况">
                {{ maritalMap[customer.marital_status] || customer.marital_status }}
              </n-descriptions-item>
              <n-descriptions-item label="工作年限">
                {{ customer.work_years }} 年
              </n-descriptions-item>
              <n-descriptions-item label="月收入">
                ¥{{ customer.monthly_income?.toLocaleString() }}
              </n-descriptions-item>
              <n-descriptions-item label="房产">
                <n-tag :type="customer.has_house ? 'success' : 'default'">
                  {{ customer.has_house ? '有' : '无' }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="车产">
                <n-tag :type="customer.has_car ? 'success' : 'default'">
                  {{ customer.has_car ? '有' : '无' }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="风险评分">
                <n-statistic :value="customer.credit_score || 0" />
              </n-descriptions-item>
              <n-descriptions-item label="风险等级">
                {{ riskLevelTag(customer.risk_level) }}
              </n-descriptions-item>
              <n-descriptions-item label="黑名单状态">
                <n-tag :type="isBlacklisted ? 'error' : 'success'">
                  {{ isBlacklisted ? '在黑名单中' : '正常' }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="居住地址" :span="2">
                {{ customer.address }}
              </n-descriptions-item>
              <n-descriptions-item label="创建时间" :span="2">
                {{ formatDate(customer.created_at) }}
              </n-descriptions-item>
            </n-descriptions>
          </n-tab-pane>

          <n-tab-pane name="loans" tab="贷款记录">
            <n-data-table
              :columns="loanColumns"
              :data="loanRecords"
              :pagination="loanPagination"
            />
          </n-tab-pane>

          <n-tab-pane name="credit" tab="信用报告">
            <div v-if="creditReports.length === 0" class="empty-state">
              <n-empty description="暂无信用报告记录" />
            </div>
            <n-timeline v-else>
              <n-timeline-item
                v-for="report in creditReports"
                :key="report.id"
                :title="`信用报告 #${report.id}`"
                :time="formatDate(report.created_at)"
              >
                <n-card size="small" class="report-card">
                  <n-descriptions :columns="2" size="small">
                    <n-descriptions-item label="征信评分">
                      <n-statistic :value="report.credit_score || 0" />
                    </n-descriptions-item>
                    <n-descriptions-item label="负债总额">
                      ¥{{ report.total_debt?.toLocaleString() || 0 }}
                    </n-descriptions-item>
                    <n-descriptions-item label="逾期次数">
                      <n-tag :type="report.overdue_count > 0 ? 'error' : 'success'">
                        {{ report.overdue_count || 0 }} 次
                      </n-tag>
                    </n-descriptions-item>
                    <n-descriptions-item label="查询记录">
                      {{ report.query_count || 0 }} 次
                    </n-descriptions-item>
                    <n-descriptions-item label="报告详情" :span="2">
                      {{ report.report_details }}
                    </n-descriptions-item>
                  </n-descriptions>
                </n-card>
              </n-timeline-item>
            </n-timeline>
          </n-tab-pane>
        </n-tabs>
      </div>
    </n-card>

    <n-modal v-model:show="showLoanModal" preset="card" title="新增贷款申请" :style="{ width: '600px' }">
      <n-form
        ref="loanFormRef"
        :model="loanFormData"
        :rules="loanFormRules"
        label-placement="left"
        label-width="100px"
      >
        <n-form-item label="贷款类型" path="loan_type">
          <n-select
            v-model:value="loanFormData.loan_type"
            :options="loanTypeOptions"
            placeholder="请选择贷款类型"
          />
        </n-form-item>
        <n-form-item label="贷款金额(元)" path="amount">
          <n-input-number
            v-model:value="loanFormData.amount"
            placeholder="请输入贷款金额"
            :min="1000"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="贷款期限(月)" path="term_months">
          <n-select
            v-model:value="loanFormData.term_months"
            :options="termOptions"
            placeholder="请选择贷款期限"
          />
        </n-form-item>
        <n-form-item label="贷款利率(%)" path="interest_rate">
          <n-input-number
            v-model:value="loanFormData.interest_rate"
            placeholder="请输入年利率"
            :min="0"
            :max="36"
            :step="0.01"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="贷款用途" path="purpose">
          <n-input
            v-model:value="loanFormData.purpose"
            type="textarea"
            placeholder="请输入贷款用途"
            :rows="3"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showLoanModal = false">取消</n-button>
          <n-button type="primary" :loading="loanSubmitting" @click="handleLoanSubmit">提交申请</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, h, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { ArrowBack, Add } from '@vicons/ionicons5'
import { getCustomerDetail } from '@/api/customer'
import { createLoanApplication, getCustomerLoanList } from '@/api/loan'
import { getCreditReportList } from '@/api/risk'
import { riskLevelTag, formatDate, applicationStatusTag } from '@/utils'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const activeTab = ref('info')
const customer = ref(null)
const isBlacklisted = ref(false)
const loanRecords = ref([])
const creditReports = ref([])

const showLoanModal = ref(false)
const loanSubmitting = ref(false)
const loanFormRef = ref(null)

const customerId = route.params.id

const loanFormData = reactive({
  loan_type: '',
  amount: null,
  term_months: null,
  interest_rate: null,
  purpose: ''
})

const loanFormRules = {
  loan_type: { required: true, message: '请选择贷款类型', trigger: 'change' },
  amount: { required: true, message: '请输入贷款金额', trigger: 'blur' },
  term_months: { required: true, message: '请选择贷款期限', trigger: 'change' },
  interest_rate: { required: true, message: '请输入贷款利率', trigger: 'blur' },
  purpose: { required: true, message: '请输入贷款用途', trigger: 'blur' }
}

const educationMap = {
  high_school: '高中及以下',
  college: '大专',
  bachelor: '本科',
  master: '硕士',
  doctor: '博士'
}

const maritalMap = {
  single: '未婚',
  married: '已婚',
  divorced: '离异',
  widowed: '丧偶'
}

const loanTypeOptions = [
  { label: '个人贷款', value: 'personal' },
  { label: '企业贷款', value: 'business' },
  { label: '抵押贷款', value: 'mortgage' },
  { label: '车贷', value: 'car' },
  { label: '消费贷款', value: 'consumer' }
]

const termOptions = [
  { label: '3个月', value: 3 },
  { label: '6个月', value: 6 },
  { label: '12个月', value: 12 },
  { label: '24个月', value: 24 },
  { label: '36个月', value: 36 },
  { label: '60个月', value: 60 }
]

const loanColumns = [
  { title: '申请编号', key: 'id', width: 100 },
  { title: '贷款类型', key: 'loan_type', width: 100, render: (row) => loanTypeOptions.find(t => t.value === row.loan_type)?.label || row.loan_type },
  { title: '贷款金额', key: 'amount', width: 120, render: (row) => `¥${row.amount?.toLocaleString()}` },
  { title: '期限', key: 'term_months', width: 80, render: (row) => `${row.term_months}个月` },
  { title: '风险评分', key: 'risk_score', width: 90 },
  { title: '状态', key: 'status', width: 120, render: (row) => applicationStatusTag(row.status) },
  { title: '申请时间', key: 'created_at', width: 180, render: (row) => formatDate(row.created_at) },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => h(
      'n-button',
      { size: 'small', onClick: () => goToLoanDetail(row.id) },
      { default: () => '详情' }
    )
  }
]

const loanPagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50]
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getCustomerDetail(customerId)
    customer.value = res.data
    isBlacklisted.value = res.data.is_blacklisted || false

    const [loansRes, reportsRes] = await Promise.all([
      getCustomerLoanList(customerId),
      getCreditReportList({ customer_id: customerId })
    ])
    loanRecords.value = loansRes.data.items || loansRes.data
    creditReports.value = reportsRes.data.items || reportsRes.data
    loanPagination.itemCount = loansRes.data.total || loanRecords.value.length
  } catch (error) {
    console.error('Failed to fetch customer detail:', error)
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

function goToLoanDetail(id) {
  router.push(`/loans/${id}`)
}

function showAddLoanModal() {
  Object.assign(loanFormData, {
    loan_type: '',
    amount: null,
    term_months: null,
    interest_rate: null,
    purpose: ''
  })
  showLoanModal.value = true
}

async function handleLoanSubmit() {
  try {
    await loanFormRef.value?.validate()
    loanSubmitting.value = true
    await createLoanApplication({
      customer_id: customerId,
      ...loanFormData
    })
    message.success('贷款申请提交成功')
    showLoanModal.value = false
    fetchData()
  } catch (error) {
    console.error('Submit loan failed:', error)
  } finally {
    loanSubmitting.value = false
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

.report-card {
  margin-top: 8px;
}
</style>
