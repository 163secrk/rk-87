<template>
  <div class="page-container">
    <n-card :bordered="false" class="filter-card">
      <n-form inline :model="filterForm">
        <n-form-item label="规则名称">
          <n-input
            v-model:value="filterForm.rule_name"
            placeholder="请输入规则名称"
            clearable
            style="width: 180px"
          />
        </n-form-item>
        <n-form-item label="规则状态">
          <n-select
            v-model:value="filterForm.status"
            :options="statusOptions"
            placeholder="全部"
            clearable
            style="width: 140px"
          />
        </n-form-item>
        <n-form-item label="动作类型">
          <n-select
            v-model:value="filterForm.action_type"
            :options="actionTypeOptions"
            placeholder="全部"
            clearable
            style="width: 160px"
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
          <span>风险规则列表</span>
          <n-button type="primary" @click="showCreateModal">
            <template #icon><n-icon><Add /></n-icon></template>
            新增规则
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
            <n-form-item label="规则名称" path="rule_name">
              <n-input v-model:value="formData.rule_name" placeholder="请输入规则名称" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="优先级" path="priority">
              <n-input-number
                v-model:value="formData.priority"
                placeholder="请输入优先级"
                :min="0"
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="条件字段" path="condition_field">
              <n-select
                v-model:value="formData.condition_field"
                :options="conditionFieldOptions"
                placeholder="请选择条件字段"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="条件运算符" path="condition_operator">
              <n-select
                v-model:value="formData.condition_operator"
                :options="operatorOptions"
                placeholder="请选择运算符"
              />
            </n-form-item>
          </n-col>
          <n-col :span="24">
            <n-form-item label="条件值" path="condition_value">
              <n-input v-model:value="formData.condition_value" placeholder="请输入条件值" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="动作类型" path="action_type">
              <n-select
                v-model:value="formData.action_type"
                :options="actionTypeOptions"
                placeholder="请选择动作类型"
                @update:value="handleActionTypeChange"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="动作值" path="action_value">
              <n-input-number
                v-model:value="formData.action_value"
                placeholder="请输入动作值"
                :min="0"
                :disabled="!isScoreAction"
                style="width: 100%"
              />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="状态" path="status">
              <n-radio-group v-model:value="formData.status">
                <n-radio value="active">启用</n-radio>
                <n-radio value="inactive">禁用</n-radio>
              </n-radio-group>
            </n-form-item>
          </n-col>
          <n-col :span="24">
            <n-form-item label="规则描述" path="description">
              <n-input
                v-model:value="formData.description"
                type="textarea"
                placeholder="请输入规则描述"
                :rows="3"
              />
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
import { ref, reactive, onMounted, h, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { Add } from '@vicons/ionicons5'
import { getRiskRuleList, createRiskRule, updateRiskRule, deleteRiskRule, toggleRiskRule } from '@/api/risk'
import { formatDateTime } from '@/utils'

const message = useMessage()

const loading = ref(false)
const submitLoading = ref(false)
const showModal = ref(false)
const modalTitle = ref('新增规则')
const editingId = ref(null)
const formRef = ref(null)

const tableData = ref([])

const filterForm = reactive({
  rule_name: '',
  status: null,
  action_type: null,
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
  rule_name: '',
  condition_field: '',
  condition_operator: '',
  condition_value: '',
  action_type: '',
  action_value: null,
  priority: 0,
  status: 'active',
  description: ''
})

const isScoreAction = computed(() => {
  return formData.action_type === 'SCORE_PLUS' || formData.action_type === 'SCORE_MINUS'
})

const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

const conditionFieldOptions = [
  { label: 'age', value: 'age' },
  { label: 'education', value: 'education' },
  { label: 'work_years', value: 'work_years' },
  { label: 'monthly_income', value: 'monthly_income' },
  { label: 'has_house', value: 'has_house' },
  { label: 'has_car', value: 'has_car' },
  { label: 'debt_to_income_ratio', value: 'debt_to_income_ratio' },
  { label: 'loan_amount', value: 'loan_amount' },
  { label: 'loan_term', value: 'loan_term' },
  { label: 'credit_score', value: 'credit_score' }
]

const operatorOptions = [
  { label: 'GT', value: 'GT' },
  { label: 'LT', value: 'LT' },
  { label: 'GTE', value: 'GTE' },
  { label: 'LTE', value: 'LTE' },
  { label: 'EQ', value: 'EQ' },
  { label: 'NEQ', value: 'NEQ' },
  { label: 'CONTAINS', value: 'CONTAINS' },
  { label: 'IN', value: 'IN' }
]

const actionTypeOptions = [
  { label: 'SCORE_PLUS', value: 'SCORE_PLUS' },
  { label: 'SCORE_MINUS', value: 'SCORE_MINUS' },
  { label: 'AUTO_APPROVE', value: 'AUTO_APPROVE' },
  { label: 'AUTO_REJECT', value: 'AUTO_REJECT' },
  { label: 'MANUAL_REVIEW', value: 'MANUAL_REVIEW' }
]

const formRules = {
  rule_name: { required: true, message: '请输入规则名称', trigger: 'blur' },
  condition_field: { required: true, message: '请选择条件字段', trigger: 'change' },
  condition_operator: { required: true, message: '请选择条件运算符', trigger: 'change' },
  condition_value: { required: true, message: '请输入条件值', trigger: 'blur' },
  action_type: { required: true, message: '请选择动作类型', trigger: 'change' },
  action_value: [
    {
      validator: (rule, value) => {
        if (isScoreAction.value && (value === null || value === undefined || value === '')) {
          return new Error('请输入动作值')
        }
        return true
      },
      trigger: 'blur'
    }
  ],
  priority: { required: true, message: '请输入优先级', trigger: 'blur' },
  status: { required: true, message: '请选择状态', trigger: 'change' }
}

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '规则名称', key: 'rule_name', width: 140, ellipsis: true },
  { title: '条件字段', key: 'condition_field', width: 130 },
  { title: '条件运算符', key: 'condition_operator', width: 120 },
  { title: '条件值', key: 'condition_value', width: 100 },
  { title: '动作类型', key: 'action_type', width: 140 },
  { title: '动作值', key: 'action_value', width: 90 },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render: (row) => h(
      'n-tag',
      { type: row.status === 'active' ? 'success' : 'default', size: 'small' },
      { default: () => row.status === 'active' ? '启用' : '禁用' }
    )
  },
  { title: '优先级', key: 'priority', width: 80 },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render: (row) => formatDateTime(row.created_at)
  },
  {
    title: '操作',
    key: 'actions',
    width: 240,
    render: (row) => [
      h('n-button', { size: 'small', onClick: () => showEditModal(row) }, { default: () => '编辑' }),
      h('n-button', { size: 'small', type: 'error', onClick: () => handleDelete(row.id), style: { marginLeft: '8px' } }, { default: () => '删除' }),
      h('n-button', {
        size: 'small',
        type: row.status === 'active' ? 'warning' : 'success',
        onClick: () => handleToggle(row.id),
        style: { marginLeft: '8px' }
      }, { default: () => row.status === 'active' ? '禁用' : '启用' })
    ]
  }
]

async function fetchData() {
  loading.value = true
  try {
    const params = { ...filterForm }
    const res = await getRiskRuleList(params)
    tableData.value = res.data.items
    pagination.itemCount = res.data.total
    pagination.page = filterForm.page
    pagination.pageSize = filterForm.page_size
  } catch (error) {
    console.error('Failed to fetch rules:', error)
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
  filterForm.rule_name = ''
  filterForm.status = null
  filterForm.action_type = null
  filterForm.page = 1
  fetchData()
}

function showCreateModal() {
  modalTitle.value = '新增规则'
  editingId.value = null
  Object.assign(formData, {
    rule_name: '',
    condition_field: '',
    condition_operator: '',
    condition_value: '',
    action_type: '',
    action_value: null,
    priority: 0,
    status: 'active',
    description: ''
  })
  showModal.value = true
}

function showEditModal(row) {
  modalTitle.value = '编辑规则'
  editingId.value = row.id
  Object.assign(formData, {
    rule_name: row.rule_name,
    condition_field: row.condition_field,
    condition_operator: row.condition_operator,
    condition_value: row.condition_value,
    action_type: row.action_type,
    action_value: row.action_value,
    priority: row.priority,
    status: row.status,
    description: row.description || ''
  })
  showModal.value = true
}

function handleActionTypeChange() {
  if (!isScoreAction.value) {
    formData.action_value = null
  }
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitLoading.value = true

    if (editingId.value) {
      await updateRiskRule(editingId.value, formData)
      message.success('更新成功')
    } else {
      await createRiskRule(formData)
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
    content: '确定要删除该规则吗？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteRiskRule(id)
        message.success('删除成功')
        fetchData()
      } catch (error) {
        console.error('Delete failed:', error)
      }
    }
  })
}

async function handleToggle(id) {
  try {
    await toggleRiskRule(id)
    message.success('状态切换成功')
    fetchData()
  } catch (error) {
    console.error('Toggle failed:', error)
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
