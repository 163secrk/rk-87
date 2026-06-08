<template>
  <div class="page-container">
    <n-card :bordered="false" class="filter-card">
      <n-form inline :model="filterForm">
        <n-form-item label="用户名">
          <n-input
            v-model:value="filterForm.username"
            placeholder="请输入用户名"
            clearable
            style="width: 160px"
          />
        </n-form-item>
        <n-form-item label="姓名">
          <n-input
            v-model:value="filterForm.name"
            placeholder="请输入姓名"
            clearable
            style="width: 160px"
          />
        </n-form-item>
        <n-form-item label="角色">
          <n-select
            v-model:value="filterForm.role"
            :options="roleOptions"
            placeholder="全部"
            clearable
            style="width: 140px"
          />
        </n-form-item>
        <n-form-item label="状态">
          <n-select
            v-model:value="filterForm.status"
            :options="statusOptions"
            placeholder="全部"
            clearable
            style="width: 120px"
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
          <span>用户列表</span>
          <n-button type="primary" @click="showCreateModal">
            <template #icon><n-icon><Add /></n-icon></template>
            新增用户
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

    <n-modal v-model:show="showModal" preset="card" :title="modalTitle" :style="{ width: '600px' }">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100px"
      >
        <n-row :gutter="20">
          <n-col :span="12">
            <n-form-item label="用户名" path="username">
              <n-input v-model:value="formData.username" placeholder="请输入用户名" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="密码" path="password">
              <n-input
                v-model:value="formData.password"
                :placeholder="editingId ? '不修改请留空' : '请输入密码'"
                :type="showPassword ? 'text' : 'password'"
              >
                <template #suffix>
                  <n-icon
                    style="cursor: pointer"
                    @click="showPassword = !showPassword"
                  >
                    <Eye v-if="!showPassword" />
                    <EyeOff v-else />
                  </n-icon>
                </template>
              </n-input>
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="姓名" path="name">
              <n-input v-model:value="formData.name" placeholder="请输入姓名" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="邮箱" path="email">
              <n-input v-model:value="formData.email" placeholder="请输入邮箱" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="手机号" path="phone">
              <n-input v-model:value="formData.phone" placeholder="请输入手机号" />
            </n-form-item>
          </n-col>
          <n-col :span="12">
            <n-form-item label="角色" path="role">
              <n-select
                v-model:value="formData.role"
                :options="roleOptions"
                placeholder="请选择角色"
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
import { useMessage } from 'naive-ui'
import { Add, Trash, Eye, EyeOff } from '@vicons/ionicons5'
import { NTag } from 'naive-ui'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/user'
import { formatDate } from '@/utils'

const message = useMessage()

const loading = ref(false)
const submitLoading = ref(false)
const showModal = ref(false)
const modalTitle = ref('新增用户')
const editingId = ref(null)
const formRef = ref(null)
const showPassword = ref(false)

const tableData = ref([])

const filterForm = reactive({
  username: '',
  name: '',
  role: null,
  status: null,
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
  username: '',
  password: '',
  name: '',
  email: '',
  phone: '',
  role: '',
  status: 'active'
})

const roleOptions = [
  { label: '系统管理员', value: 'admin' },
  { label: '风控经理', value: 'manager' },
  { label: '审核员', value: 'reviewer' },
  { label: '操作员', value: 'operator' }
]

const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

const roleMap = {
  admin: '系统管理员',
  manager: '风控经理',
  reviewer: '审核员',
  operator: '操作员'
}

const statusTag = (status) => {
  if (status === 'active') {
    return h(NTag, { type: 'success', size: 'small' }, { default: () => '启用' })
  }
  return h(NTag, { type: 'error', size: 'small' }, { default: () => '禁用' })
}

const formRules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: [
    {
      validator: (rule, value) => {
        if (!editingId.value && !value) {
          return new Error('请输入密码')
        }
        return true
      },
      trigger: 'blur'
    }
  ],
  name: { required: true, message: '请输入姓名', trigger: 'blur' },
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: { required: true, message: '请选择角色', trigger: 'change' }
}

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '用户名', key: 'username', width: 120 },
  { title: '姓名', key: 'name', width: 100 },
  {
    title: '角色',
    key: 'role',
    width: 120,
    render: (row) => roleMap[row.role] || row.role
  },
  { title: '邮箱', key: 'email', width: 180, ellipsis: true },
  { title: '手机号', key: 'phone', width: 130 },
  {
    title: '状态',
    key: 'status',
    width: 80,
    render: (row) => statusTag(row.status)
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
    render: (row) => formatDate(row.created_at, 'YYYY-MM-DD HH:mm:ss')
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row) => [
      h('n-button', { size: 'small', onClick: () => showEditModal(row) }, { default: () => '编辑' }),
      h('n-button', { size: 'small', type: 'error', onClick: () => handleDelete(row.id), style: { marginLeft: '8px' } }, { default: () => '删除' })
    ]
  }
]

async function fetchData() {
  loading.value = true
  try {
    const params = { ...filterForm }
    const res = await getUserList(params)
    tableData.value = res.data.items
    pagination.itemCount = res.data.total
    pagination.page = filterForm.page
    pagination.pageSize = filterForm.page_size
  } catch (error) {
    console.error('Failed to fetch users:', error)
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
  filterForm.username = ''
  filterForm.name = ''
  filterForm.role = null
  filterForm.status = null
  filterForm.page = 1
  fetchData()
}

function showCreateModal() {
  modalTitle.value = '新增用户'
  editingId.value = null
  showPassword.value = false
  Object.assign(formData, {
    username: '',
    password: '',
    name: '',
    email: '',
    phone: '',
    role: '',
    status: 'active'
  })
  showModal.value = true
}

function showEditModal(row) {
  modalTitle.value = '编辑用户'
  editingId.value = row.id
  showPassword.value = false
  Object.assign(formData, {
    username: row.username,
    password: '',
    name: row.name,
    email: row.email,
    phone: row.phone,
    role: row.role,
    status: row.status
  })
  showModal.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitLoading.value = true

    const data = { ...formData }
    if (editingId.value && !data.password) {
      delete data.password
    }

    if (editingId.value) {
      await updateUser(editingId.value, data)
      message.success('更新成功')
    } else {
      await createUser(data)
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
    content: '确定要删除该用户吗？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteUser(id)
        message.success('删除成功')
        fetchData()
      } catch (error) {
        console.error('Delete failed:', error)
      }
    }
  })
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
