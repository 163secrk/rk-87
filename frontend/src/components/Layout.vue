<template>
  <n-layout has-sider>
    <n-layout-sider
      :collapsed-width="64"
      :width="240"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="logo" :class="{ collapsed }">
        <span v-if="!collapsed" class="logo-text">金盾信贷</span>
        <span v-else class="logo-icon">盾</span>
      </div>
      <n-menu
        :value="activeMenu"
        :options="menuOptions"
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        @update:value="handleMenuClick"
      />
    </n-layout-sider>
    <n-layout>
      <n-layout-header class="header">
        <div class="header-left">
          <span class="page-title">{{ currentPageTitle }}</span>
        </div>
        <div class="header-right">
          <n-dropdown trigger="hover" :options="userOptions" @select="handleSelect">
            <div class="user-info">
              <n-avatar size="small">
                {{ userStore.userInfo?.full_name?.charAt(0) || 'U' }}
              </n-avatar>
              <span class="user-name">{{ userStore.userInfo?.full_name }}</span>
              <span class="user-role">({{ getRoleText(userStore.userInfo?.role) }})</span>
              <n-icon><ChevronDown /></n-icon>
            </div>
          </n-dropdown>
        </div>
      </n-layout-header>
      <n-layout-content class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { useUserStore } from '@/stores/user'
import { setMessageInstance } from '@/utils/request'
import { getRoleText } from '@/utils'
import {
  Dashboard,
  People,
  FileTrayFull,
  Settings,
  Ban,
  Document,
  Person,
  ChevronDown,
  LogOut,
  PersonCircle
} from '@vicons/ionicons5'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const userStore = useUserStore()

const collapsed = ref(false)
const activeMenu = ref('')

onMounted(() => {
  setMessageInstance(message)
  activeMenu.value = route.name
})

const menuOptions = computed(() => {
  const userRole = userStore.userInfo?.role
  const items = [
    {
      label: '仪表盘',
      key: 'Dashboard',
      icon: () => h(Dashboard)
    },
    {
      label: '客户管理',
      key: 'Customers',
      icon: () => h(People)
    },
    {
      label: '贷款申请',
      key: 'Loans',
      icon: () => h(FileTrayFull)
    },
    {
      label: '风控管理',
      key: 'risk',
      icon: () => h(Settings),
      children: [
        {
          label: '风控规则',
          key: 'RiskRules',
          icon: () => h(Settings)
        },
        {
          label: '黑名单管理',
          key: 'Blacklist',
          icon: () => h(Ban)
        },
        {
          label: '信用报告',
          key: 'CreditReports',
          icon: () => h(Document)
        }
      ]
    }
  ]

  if (userRole === 'admin' || userRole === 'manager') {
    items.push({
      label: '系统管理',
      key: 'system',
      icon: () => h(Person),
      children: [
        {
          label: '用户管理',
          key: 'Users',
          icon: () => h(Person)
        }
      ]
    })
  }

  return items
})

import { h } from 'vue'

const currentPageTitle = computed(() => {
  return route.meta.title || ''
})

const userOptions = computed(() => [
  {
    label: '个人信息',
    key: 'profile',
    icon: () => h(PersonCircle)
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(LogOut)
  }
])

function handleMenuClick(key) {
  activeMenu.value = key
  router.push({ name: key })
}

function handleSelect(key) {
  if (key === 'logout') {
    dialog.warning({
      title: '确认退出',
      content: '您确定要退出登录吗？',
      positiveText: '确定',
      negativeText: '取消',
      onPositiveClick: () => {
        userStore.logout()
        router.push('/login')
        message.success('已退出登录')
      }
    })
  }
}
</script>

<style scoped lang="scss">
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  font-weight: 600;

  &.collapsed .logo-icon {
    display: block;
  }

  .logo-text {
    font-size: 18px;
    letter-spacing: 2px;
  }

  .logo-icon {
    display: none;
    font-size: 24px;
    font-weight: bold;
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;

  .header-left {
    .page-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 6px;
      transition: background 0.2s;

      &:hover {
        background: #f5f5f5;
      }

      .user-name {
        color: #333;
        font-size: 14px;
      }

      .user-role {
        color: #999;
        font-size: 12px;
      }
    }
  }
}

.content {
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
