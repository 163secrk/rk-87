<template>
  <div class="not-found">
    <div class="content">
      <h1 class="code">404</h1>
      <p class="message">页面不存在或已被移除</p>
      <n-button type="primary" @click="goHome">返回首页</n-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;

  .content {
    text-align: center;

    .code {
      font-size: 120px;
      font-weight: 700;
      color: #3b82f6;
      margin-bottom: 16px;
      text-shadow: 2px 2px 4px rgba(59, 130, 246, 0.2);
    }

    .message {
      font-size: 18px;
      color: #64748b;
      margin-bottom: 32px;
    }
  }
}
</style>
