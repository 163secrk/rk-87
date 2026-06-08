<template>
  <div class="page-container">
    <n-card :bordered="false" class="filter-card">
      <n-form inline :model="filterForm">
        <n-form-item label="客户姓名">
          <n-input
            v-model:value="filterForm.name"
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
        <n-form-item label="手机号">
          <n-input
            v-model:value="filterForm.phone"
            placeholder="请输入手机号"
            clearable
            style="width: 160px"
          />
        </n-form-item>
        <n-form-item label="原因类型">
          <n-select
            v-model:value="filterForm.reason_type"
            :options="reasonTypeOptions"
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
          <span>黑名单列表</span>
          <n-button type="primary" @click="showCreateModal">
            <template #icon><n-icon><Add /></n-icon></template>
            加入黑名单
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

    <n-modal v-model:show="showModal" preset="card" title="加入黑名单" :style="{ width: '600px' }">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100px"
      >
        <n-form-item label="客户" path="customer_id">
          <n-select
            v-model:value="formData.customer_id"
            :options="customerOptions"
            :loading="customerLoading"
            :on-search="handleCustomerSearch"
            filterable
            placeholder="请搜索客户"
            clearable
          />
        </n-form-item>
        <n-form-item label="原因类型" path="reason_type">
          <n-select
            v-model:value="formData.reason_type"
            :options="reasonTypeOptions"
            placeholder="请选择原因类型"
          />
        </n-form-item>
        <n-form-item label="原因描述" path="reason_description">
          <n-input
            v-model:value="formData.reason_description"
            type="textarea"
            :rows="4"
            placeholder="请输入原因描述"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { Add, Eye, Trash } from '@vicons/ionicons5'
import { getBlacklist, addBlacklist as addToBlacklist, removeBlacklist as removeFromBlacklist } from '@/api/risk'
import { getCustomerList } from '@/api/customer'
import { formatDate, getBlacklistTypeText } from '@/utils'

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const submitLoading = ref(false)
const customerLoading = ref(false)
const showModal = ref(false)
const formRef = ref(null)

const tableData = ref([])
const customerOptions = ref([])

const filterForm = reactive({
  name: '',
  id_card: '',
  phone: '',
  reason_type: null,
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
  reason_type: '',
  reason_description: ''
})

const formRules = {
  customer_id: { required: true, message: '请选择客户', trigger: 'change' },
  reason_type: { required: true, message: '请选择原因类型', trigger: 'change' },
  reason_description: { required: true, message: '请输入原因描述', trigger: 'blur' }
}

const reasonTypeOptions = [
  { label: '欺诈', value: 'fraud' },
  { label: '逾期', value: 'overdue' },
  { label: '信用不良', value: 'bad_credit' },
  { label: '其他', value: 'other' }
]

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '客户姓名', key: 'customer_name', width: 100 },
  { title: '身份证号', key: 'id_card', width: 180, ellipsis: true },
  { title: '手机号', key: 'phone', width: 120 },
  {
    title: '原因类型',
    key: 'reason_type',
    width: 100,
    render: (row) => getBlacklistTypeText(row.reason_type)
  },
  { title: '原因描述', key: 'reason_description', ellipsis: true },
  {
    title: '加入时间',
    key: 'created_at',
    width: 160,
    render: (row) => formatDate(row.created_at, 'YYYY-MM-DD HH:mm:ss')
  },
  { title: '操作人', key: 'operator_name', width: 100 },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) => [
      h(
        'n-button',
        { size: 'small', onClick: () => viewDetail(row.customer_id) },
        { default: () => '查看详情' }
      ),
      h(
        'n-button',
        {
          size: 'small',
          type: 'error',
          onClick: () => handleRemove(row.id),
          style: { marginLeft: '8px' }
        },
        { default: () => '移除黑名单' }
      )
    ]
  }
]

async function fetchData() {
  loading.value = true
  try {
    const params = { ...filterForm }
    const res = await getBlacklist(params)
    tableData.value = res.data.items
    pagination.itemCount = res.data.total
    pagination.page = filterForm.page
    pagination.pageSize = filterForm.page_size
  } catch (error) {
    console.error('Failed to fetch blacklist:', error)
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
  filterForm.name = ''
  filterForm.id_card = ''
  filterForm.phone = ''
  filterForm.reason_type = null
  filterForm.page = 1
  fetchData()
}

function showCreateModal() {
  Object.assign(formData, {
    customer_id: null,
    reason_type: '',
    reason_description: ''
  })
  customerOptions.value = []
  showModal.value = true
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

    await addToBlacklist(formData)
    message.success('加入黑名单成功')

    showModal.value = false
    fetchData()
  } catch (error) {
    console.error('Submit failed:', error)
  } finally {
    submitLoading.value = false
  }
}

async function handleRemove(id) {
  window.$dialog.warning({
    title: '确认移除',
    content: '确定要将该客户从黑名单中移除吗？',
    positiveText: '移除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await removeFromBlacklist(id)
        message.success('移除成功')
        fetchData()
      } catch (error) {
        console.error('Remove failed:', error)
      }
    }
  })
}

function viewDetail(customerId) {
  router.push(`/customers/${customerId}`)
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
