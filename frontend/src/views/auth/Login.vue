<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo">
          <span class="logo-icon">盾</span>
        </div>
        <h1 class="title">金盾信贷风控审批系统</h1>
        <p class="subtitle">Jindun Credit Risk Management System</p>
      </div>

      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        class="login-form"
        @submit="handleLogin"
      >
        <n-form-item path="username">
          <n-input
            v-model:value="formData.username"
            placeholder="请输入用户名"
            size="large"
            clearable
          >
            <template #prefix>
              <n-icon><Person /></n-icon>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item path="password">
          <n-input
            v-model:value="formData.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password-on="click"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <n-icon><LockClosed /></n-icon>
            </template>
          </n-input>
        </n-form-item>

        <n-button
          type="primary"
          size="large"
          block
          :loading="loading"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </n-button>
      </n-form>

      <div class="login-footer">
        <p>默认账号: admin / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useUserStore } from '@/stores/user'
import { setMessageInstance } from '@/utils/request'
import { Person, LockClosed } from '@vicons/ionicons5'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

onMounted(() => {
  setMessageInstance(message)
})

const formRef = ref(null)
const loading = ref(false)

const formData = reactive({
  username: 'admin',
  password: '123456'
})

const rules = {
  username: {
    required: true,
    message: '请输入用户名',
    trigger: 'blur'
  },
  password: {
    required: true,
    message: '请输入密码',
    trigger: 'blur'
  }
}

async function handleLogin() {
  if (!formData.username || !formData.password) {
    message.warning('请输入用户名和密码')
    return
  }

  try {
    loading.value = true
    await userStore.login(formData.username, formData.password)
    message.success('登录成功')
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    console.error('Login failed:', error)
    message.error(error.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    width: 600px;
    height: 600px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 50%;
    top: -200px;
    left: -200px;
  }

  &::after {
    content: '';
    position: absolute;
    width: 500px;
    height: 500px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 50%;
    bottom: -150px;
    right: -150px;
  }
}

.login-box {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 10;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;

  .logo {
    width: 72px;
    height: 72px;
    margin: 0 auto 16px;
    background: linear-gradient(135deg, #1e40af, #3b82f6);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);

    .logo-icon {
      color: #fff;
      font-size: 36px;
      font-weight: bold;
    }
  }

  .title {
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 13px;
    color: #64748b;
    letter-spacing: 1px;
  }
}

.login-form {
  :deep(.n-form-item) {
    margin-bottom: 20px;
  }
}

.login-footer {
  margin-top: 24px;
  text-align: center;

  p {
    font-size: 12px;
    color: #94a3b8;
  }
}
</style>
