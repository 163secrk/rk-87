<template>
  <div class="page-container">
    <n-card :bordered="false" class="filter-card">
      <n-form inline :model="filterForm">
        <n-form-item label="客户姓名">
          <n-input
            v-model:value="filterForm.customer_name"
            placeholder="请输入姓名"
            clearable
            style="width: 180px"
          />
        </n-form-item>
        <n-form-item label="身份证号">
          <n-input
            v-model:value="filterForm.id_card"
            placeholder="请输入身份证号"
            clearable
            style="width: 200px"
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
          <span>信用报告列表</span>
          <n-button type="primary" @click="showCreateModal">
            <template #icon><n-icon><Add /></n-icon></template>
            新增报告
          </n-button>
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

    <n-modal v-model:show="showCreateModalFlag" preset="card" title="新增信用报告" :style="{ width: '600px' }">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100px"
      >
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="客户" path="customer_id">
              <n-select
                v-model:value="formData.customer_id"
                :options="customerOptions"
                :loading="customerLoading"
                :on-search="handleCustomerSearch"
                filterable
                remote
                placeholder="请搜索客户"
                clearable
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="征信评分" path="credit_score">
              <n-input-number
                v-model:value="formData.credit_score"
                placeholder="请输入征信评分"
                :min="0"
                :max="1000"
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="负债总额" path="total_debt">
              <n-input-number
                v-model:value="formData.total_debt"
                placeholder="请输入负债总额"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="逾期次数" path="overdue_count">
              <n-input-number
                v-model:value="formData.overdue_count"
                placeholder="请输入逾期次数"
                :min="0"
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="24">
            <n-form-item label="查询次数" path="query_count">
              <n-input-number
                v-model:value="formData.query_count"
                placeholder="请输入查询次数"
                :min="0"
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="24">
            <n-form-item label="报告详情" path="report_detail">
              <n-input
                v-model:value="formData.report_detail"
                type="textarea"
                placeholder="请输入报告详情"
                :rows="5"
              />
            </n-form-item>
          </n-col>
        </n-row>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModalFlag = false">取消</n-button>
          <n-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal v-model:show="showDetailModal" preset="card" title="信用报告详情" :style="{ width: '700px' }">
      <n-descriptions bordered :column="2" size="medium">
        <n-descriptions-item label="ID">
          {{ detailData.id }}
        </n-descriptions-item>
        <n-descriptions-item label="客户姓名">
          {{ detailData.customer_name }}
        </n-descriptions-item>
        <n-descriptions-item label="身份证号">
          {{ detailData.id_card }}
        </n-descriptions-item>
        <n-descriptions-item label="征信评分">
          {{ detailData.credit_score }}
        </n-descriptions-item>
        <n-descriptions-item label="负债总额">
          ¥{{ detailData.total_debt?.toLocaleString() || 0 }}
        </n-descriptions-item>
        <n-descriptions-item label="逾期次数">
          {{ detailData.overdue_count || 0 }}
        </n-descriptions-item>
        <n-descriptions-item label="查询次数">
          {{ detailData.query_count || 0 }}
        </n-descriptions-item>
        <n-descriptions-item label="报告日期">
          {{ formatDate(detailData.report_date) }}
        </n-descriptions-item>
        <n-descriptions-item label="创建时间">
          {{ formatDate(detailData.created_at, 'YYYY-MM-DD HH:mm:ss') }}
        </n-descriptions-item>
        <n-descriptions-item label="更新时间">
          {{ formatDate(detailData.updated_at, 'YYYY-MM-DD HH:mm:ss') }}
        </n-descriptions-item>
        <n-descriptions-item label="报告详情" :span="2">
          <div class="report-detail">{{ detailData.report_detail || '-' }}</div>
        </n-descriptions-item>
      </n-descriptions>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showDetailModal = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { useMessage } from 'naive-ui'
import { Add } from '@vicons/ionicons5'
import { getCreditReportList, createCreditReport } from '@/api/risk'
import { getCustomerList } from '@/api/customer'
import { formatDate } from '@/utils'

const message = useMessage()

const loading = ref(false)
const submitLoading = ref(false)
const customerLoading = ref(false)
const showCreateModalFlag = ref(false)
const showDetailModal = ref(false)
const formRef = ref(null)

const tableData = ref([])
const customerOptions = ref([])
const detailData = reactive({})

const filterForm = reactive({
  customer_name: '',
  id_card: '',
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

const formData = reactive({
  customer_id: null,
  credit_score: null,
  total_debt: null,
  overdue_count: null,
  query_count: null,
  report_detail: ''
})

function validateNumber(rule, value) {
  if (value === null || value === undefined || value === '') {
    return new Error(rule.message)
  }
  return true
}

const formRules = {
  customer_id: { required: true, message: '请选择客户', trigger: 'change' },
  credit_score: { validator: validateNumber, message: '请输入征信评分', trigger: 'change' }
}

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '客户姓名', key: 'customer_name', width: 100 },
  { title: '身份证号', key: 'id_card', width: 180, ellipsis: true },
  { title: '征信评分', key: 'credit_score', width: 100 },
  {
    title: '负债总额',
    key: 'total_debt',
    width: 120,
    render: (row) => `¥${row.total_debt?.toLocaleString() || 0}`
  },
  { title: '逾期次数', key: 'overdue_count', width: 90 },
  { title: '查询次数', key: 'query_count', width: 90 },
  {
    title: '报告日期',
    key: 'report_date',
    width: 120,
    render: (row) => formatDate(row.report_date)
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) =>
      h('n-button', { size: 'small', onClick: () => showDetail(row) }, { default: () => '查看详情' })
  }
]

async function fetchData() {
  loading.value = true
  try {
    const params = { ...filterForm }
    const res = await getCreditReportList(params)
    tableData.value = res.data.items
    pagination.itemCount = res.data.total
    pagination.page = filterForm.page
    pagination.pageSize = filterForm.page_size
  } catch (error) {
    console.error('Failed to fetch credit reports:', error)
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
  filterForm.id_card = ''
  filterForm.page = 1
  fetchData()
}

function showCreateModal() {
  Object.assign(formData, {
    customer_id: null,
    credit_score: null,
    total_debt: null,
    overdue_count: null,
    query_count: null,
    report_detail: ''
  })
  customerOptions.value = []
  showCreateModalFlag.value = true
}

async function handleCustomerSearch(query) {
  if (!query) {
    customerOptions.value = []
    return
  }
  customerLoading.value = true
  try {
    const res = await getCustomerList({ keyword: query, page_size: 20 })
    customerOptions.value = res.data.items.map((item) => ({
      label: `${item.name} - ${item.id_card}`,
      value: item.id
    }))
  } catch (error) {
    console.error('Failed to search customers:', error)
  } finally {
    customerLoading.value = false
  }
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitLoading.value = true

    const submitData = {
      customer_id: formData.customer_id,
      credit_score: formData.credit_score,
      total_loan_amount: formData.total_debt,
      overdue_count: formData.overdue_count || 0,
      query_count_last_30d: formData.query_count,
      report_data: formData.report_detail
    }
    await createCreditReport(submitData)
    message.success('创建成功')

    showCreateModalFlag.value = false
    fetchData()
  } catch (error) {
    console.error('Submit failed:', error)
  } finally {
    submitLoading.value = false
  }
}

function showDetail(row) {
  Object.assign(detailData, row)
  showDetailModal.value = true
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

.report-detail {
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
  line-height: 1.6;
}
</style>
