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
          <span>客户列表</span>
          <n-button type="primary" @click="showCreateModal">
            <template #icon><n-icon><Add /></n-icon></template>
            新增客户
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

    <n-modal v-model:show="showModal" preset="card" :title="modalTitle" :style="{ width: '700px' }">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100px"
      >
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="客户姓名" path="name">
              <n-input v-model:value="formData.name" placeholder="请输入姓名" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="性别" path="gender">
              <n-radio-group v-model:value="formData.gender">
                <n-radio value="male">男</n-radio>
                <n-radio value="female">女</n-radio>
              </n-radio-group>
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="身份证号" path="id_card">
              <n-input v-model:value="formData.id_card" placeholder="请输入身份证号" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="手机号" path="phone">
              <n-input v-model:value="formData.phone" placeholder="请输入手机号" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="学历" path="education">
              <n-select
                v-model:value="formData.education"
                :options="educationOptions"
                placeholder="请选择学历"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="婚姻状况" path="marital_status">
              <n-select
                v-model:value="formData.marital_status"
                :options="maritalOptions"
                placeholder="请选择"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="月收入(元)" path="monthly_income">
              <n-input-number
                v-model:value="formData.monthly_income"
                placeholder="请输入月收入"
                :min="0"
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="工作年限" path="work_years">
              <n-input-number
                v-model:value="formData.work_years"
                placeholder="请输入工作年限"
                :min="0"
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="有无房产" path="has_house">
              <n-switch v-model:value="formData.has_house" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="有无车产" path="has_car">
              <n-switch v-model:value="formData.has_car" />
            </n-form-item>
          </n-col>
          <n-col :span="24">
            <n-form-item label="居住地址">
              <n-input v-model:value="formData.address" placeholder="请输入居住地址" />
            </n-form-item>
          </n-col>
        </n-row>
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
import { getCustomerList, createCustomer, updateCustomer, deleteCustomer } from '@/api/customer'
import { riskLevelTag } from '@/utils'

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const submitLoading = ref(false)
const showModal = ref(false)
const modalTitle = ref('新增客户')
const editingId = ref(null)
const formRef = ref(null)

const tableData = ref([])

const filterForm = reactive({
  name: '',
  id_card: '',
  phone: '',
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

const formData = reactive({
  name: '',
  gender: 'male',
  id_card: '',
  phone: '',
  education: '',
  marital_status: '',
  monthly_income: null,
  work_years: null,
  has_house: false,
  has_car: false,
  address: ''
})

function validateNumber(rule, value) {
  if (value === null || value === undefined || value === '') {
    return new Error(rule.message)
  }
  return true
}

function validateSelect(rule, value) {
  if (!value || value === '') {
    return new Error(rule.message)
  }
  return true
}

function validatePhone(rule, value) {
  if (!value || value === '') {
    return new Error('请输入手机号')
  }
  const phoneReg = /^1[3-9]\d{9}$/
  if (!phoneReg.test(value)) {
    return new Error('请输入正确的手机号格式')
  }
  return true
}

const formRules = {
  name: { required: true, message: '请输入客户姓名', trigger: 'blur' },
  gender: { required: true, message: '请选择性别', trigger: 'change' },
  id_card: { required: true, message: '请输入身份证号', trigger: 'blur' },
  phone: { validator: validatePhone, trigger: 'blur' },
  education: { validator: validateSelect, message: '请选择学历', trigger: 'change' },
  marital_status: { validator: validateSelect, message: '请选择婚姻状况', trigger: 'change' },
  monthly_income: { validator: validateNumber, message: '请输入月收入', trigger: 'change' },
  work_years: { validator: validateNumber, message: '请输入工作年限', trigger: 'change' }
}

const riskLevelOptions = [
  { label: '低风险', value: 'low' },
  { label: '中低风险', value: 'medium_low' },
  { label: '中风险', value: 'medium' },
  { label: '中高风险', value: 'medium_high' },
  { label: '高风险', value: 'high' },
  { label: '极高风险', value: 'extreme_high' }
]

const educationOptions = [
  { label: '高中及以下', value: 'high_school' },
  { label: '大专', value: 'college' },
  { label: '本科', value: 'bachelor' },
  { label: '硕士', value: 'master' },
  { label: '博士', value: 'doctor' }
]

const maritalOptions = [
  { label: '未婚', value: 'single' },
  { label: '已婚', value: 'married' },
  { label: '离异', value: 'divorced' },
  { label: '丧偶', value: 'widowed' }
]

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '客户姓名', key: 'name', width: 100 },
  { title: '性别', key: 'gender', width: 70, render: (row) => row.gender === 'male' ? '男' : '女' },
  { title: '身份证号', key: 'id_card', width: 180, ellipsis: true },
  { title: '手机号', key: 'phone', width: 120 },
  { title: '月收入', key: 'monthly_income', width: 120, render: (row) => `¥${row.monthly_income?.toLocaleString() || 0}` },
  { title: '工作年限', key: 'work_years', width: 90, render: (row) => `${row.work_years || 0}年` },
  { title: '风险评分', key: 'credit_score', width: 90 },
  {
    title: '风险等级',
    key: 'risk_level',
    width: 110,
    render: (row) => riskLevelTag(row.risk_level)
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) => [
      h('n-button', { size: 'small', onClick: () => viewDetail(row.id) }, { default: () => '详情' }),
      h('n-button', { size: 'small', onClick: () => showEditModal(row), style: { marginLeft: '8px' } }, { default: () => '编辑' }),
      h('n-button', { size: 'small', type: 'error', onClick: () => handleDelete(row.id), style: { marginLeft: '8px' } }, { default: () => '删除' })
    ]
  }
]

async function fetchData() {
  loading.value = true
  try {
    const params = { ...filterForm }
    if (params.name || params.id_card || params.phone) {
      params.keyword = params.name || params.id_card || params.phone
    }
    delete params.name
    delete params.id_card
    delete params.phone
    const res = await getCustomerList(params)
    tableData.value = res.data.items
    pagination.itemCount = res.data.total
    pagination.page = filterForm.page
    pagination.pageSize = filterForm.page_size
  } catch (error) {
    console.error('Failed to fetch customers:', error)
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
  filterForm.risk_level = null
  filterForm.page = 1
  fetchData()
}

function showCreateModal() {
  modalTitle.value = '新增客户'
  editingId.value = null
  Object.assign(formData, {
    name: '',
    gender: 'male',
    id_card: '',
    phone: '',
    education: '',
    marital_status: '',
    monthly_income: null,
    work_years: null,
    has_house: false,
    has_car: false,
    address: ''
  })
  showModal.value = true
}

function showEditModal(row) {
  modalTitle.value = '编辑客户'
  editingId.value = row.id
  Object.assign(formData, {
    name: row.name,
    gender: row.gender,
    id_card: row.id_card,
    phone: row.phone,
    education: row.education,
    marital_status: row.marital_status,
    monthly_income: row.monthly_income,
    work_years: row.work_years,
    has_house: row.has_house,
    has_car: row.has_car,
    address: row.address
  })
  showModal.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitLoading.value = true

    if (editingId.value) {
      await updateCustomer(editingId.value, formData)
      message.success('更新成功')
    } else {
      await createCustomer(formData)
      message.success('创建成功')
    }

    showModal.value = false
    fetchData()
  } catch (error) {
    console.error('Submit failed:', error)
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(id) {
  window.$dialog.warning({
    title: '确认删除',
    content: '确定要删除该客户吗？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteCustomer(id)
        message.success('删除成功')
        fetchData()
      } catch (error) {
        console.error('Delete failed:', error)
      }
    }
  })
}

function viewDetail(id) {
  router.push(`/customers/${id}`)
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
