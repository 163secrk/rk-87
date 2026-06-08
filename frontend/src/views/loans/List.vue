<template>
  <div class="page-container">
    <n-card :bordered="false" class="filter-card">
      <n-form inline :model="filterForm">
        <n-form-item label="客户姓名">
          <n-input
            v-model:value="filterForm.customer_name"
            placeholder="请输入客户姓名"
            clearable
            style="width: 180px"
          />
        </n-form-item>
        <n-form-item label="贷款类型">
          <n-select
            v-model:value="filterForm.loan_type"
            :options="loanTypeOptions"
            placeholder="全部"
            clearable
            style="width: 140px"
          />
        </n-form-item>
        <n-form-item label="申请状态">
          <n-select
            v-model:value="filterForm.status"
            :options="statusOptions"
            placeholder="全部"
            clearable
            style="width: 140px"
          />
        </n-form-item>
        <n-form-item label="风险等级">
          <n-select
            v-model:value="filterForm.risk_level"
            :options="riskLevelOptions"
            placeholder="全部"
            clearable
            style="width: 140px"
          />
        </n-form-item>
        <n-form-item>
          <n-space>
            <n-button type="primary" @click="fetchData">查询</n-button>
            <n-button @click="resetFilter">重置</n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card :bordered="false" class="table-card">
      <template #header>
        <div class="card-header">
          <span>贷款申请列表</span>
        </div>
      </template>

      <n-data-table
        :columns="columns"
        :data="tableData"
        :loading="loading"
        :pagination="pagination"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </n-card>

    <n-modal v-model:show="showApproveModal" preset="card" title="审批贷款申请" :style="{ width: '500px' }">
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
          <n-button type="primary" :loading="submitLoading" @click="handleApprove">通过</n-button>
          <n-button type="error" :loading="submitLoading" @click="handleReject">拒绝</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { Eye, Checkmark, Close } from '@vicons/ionicons5'
import { getLoanApplicationList, approveLoanApplication, rejectLoanApplication } from '@/api/loan'
import { applicationStatusTag, riskLevelTag, formatDate, formatMoney } from '@/utils'

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const showApproveModal = ref(false)
const approveFormRef = ref(null)
const currentApplicationId = ref(null)

const filterForm = reactive({
  customer_name: '',
  loan_type: null,
  status: null,
  risk_level: null,
  page: 1,
  page_size: 10
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  itemCount: 0
})

const approveFormData = reactive({
  comments: ''
})

const approveFormRules = {
  comments: { required: true, message: '请输入审批意见', trigger: 'blur' }
}

const loanTypeOptions = [
  { label: '个人贷款', value: 'personal' },
  { label: '企业贷款', value: 'business' },
  { label: '抵押贷款', value: 'mortgage' },
  { label: '车贷', value: 'car' },
  { label: '消费贷款', value: 'consumer' }
]

const statusOptions = [
  { label: '待审核', value: 'pending' },
  { label: '自动通过', value: 'auto_approved' },
  { label: '自动拒绝', value: 'auto_rejected' },
  { label: '人工审核', value: 'manual_review' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' }
]

const riskLevelOptions = [
  { label: '低风险', value: 'low' },
  { label: '中低风险', value: 'medium_low' },
  { label: '中风险', value: 'medium' },
  { label: '中高风险', value: 'medium_high' },
  { label: '高风险', value: 'high' },
  { label: '极高风险', value: 'extreme_high' }
]

const columns = [
  { title: '申请编号', key: 'id', width: 100 },
  { title: '客户姓名', key: 'customer_name', width: 120 },
  {
    title: '贷款类型',
    key: 'loan_type',
    width: 110,
    render: (row) => loanTypeOptions.find(t => t.value === row.loan_type)?.label || row.loan_type
  },
  {
    title: '贷款金额',
    key: 'amount',
    width: 130,
    render: (row) => `¥${formatMoney(row.amount)}`
  },
  {
    title: '期限',
    key: 'term_months',
    width: 90,
    render: (row) => `${row.term_months}个月`
  },
  { title: '风险评分', key: 'risk_score', width: 100 },
  {
    title: '风险等级',
    key: 'risk_level',
    width: 120,
    render: (row) => riskLevelTag(row.risk_level)
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
    render: (row) => applicationStatusTag(row.status)
  },
  {
    title: '申请时间',
    key: 'created_at',
    width: 180,
    render: (row) => formatDate(row.created_at, 'YYYY-MM-DD HH:mm:ss')
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) => {
      const buttons = [
        h('n-button', { size: 'small', onClick: () => viewDetail(row.id) }, {
          default: () => '详情',
          icon: () => h('n-icon', null, { default: () => h(Eye) })
        })
      ]
      if (row.status === 'manual_review' || row.status === 'pending') {
        buttons.push(
          h('n-button', {
            size: 'small',
            type: 'primary',
            onClick: () => showApproveDialog(row.id),
            style: { marginLeft: '8px' }
          }, {
            default: () => '审批',
            icon: () => h('n-icon', null, { default: () => h(Checkmark) })
          })
        )
      }
      return buttons
    }
  }
]

async function fetchData() {
  loading.value = true
  try {
    const params = { ...filterForm }
    const res = await getLoanApplicationList(params)
    tableData.value = res.data.items
    pagination.itemCount = res.data.total
    pagination.page = filterForm.page
    pagination.pageSize = filterForm.page_size
  } catch (error) {
    console.error('Failed to fetch loan applications:', error)
  } finally {
    loading.value = false
  }
}

function handlePageChange(page) {
  filterForm.page = page
  fetchData()
}

function handlePageSizeChange(pageSize) {
  filterForm.page_size = pageSize
  filterForm.page = 1
  fetchData()
}

function resetFilter() {
  filterForm.customer_name = ''
  filterForm.loan_type = null
  filterForm.status = null
  filterForm.risk_level = null
  filterForm.page = 1
  fetchData()
}

function viewDetail(id) {
  router.push(`/loans/${id}`)
}

function showApproveDialog(id) {
  currentApplicationId.value = id
  approveFormData.comments = ''
  showApproveModal.value = true
}

async function handleApprove() {
  try {
    await approveFormRef.value?.validate()
    submitLoading.value = true
    await approveLoanApplication(currentApplicationId.value, {
      comments: approveFormData.comments
    })
    message.success('审批通过成功')
    showApproveModal.value = false
    fetchData()
  } catch (error) {
    console.error('Approve failed:', error)
  } finally {
    submitLoading.value = false
  }
}

async function handleReject() {
  try {
    await approveFormRef.value?.validate()
    submitLoading.value = true
    await rejectLoanApplication(currentApplicationId.value, {
      comments: approveFormData.comments
    })
    message.success('审批拒绝成功')
    showApproveModal.value = false
    fetchData()
  } catch (error) {
    console.error('Reject failed:', error)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.filter-card {
  border-radius: 12px;
  margin-bottom: 20px;

  :deep(.n-form-item) {
    margin-bottom: 0;
  }
}

.table-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
</style>
