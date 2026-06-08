import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: { title: '仪表盘', icon: 'dashboard' }
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customers/List.vue'),
        meta: { title: '客户管理', icon: 'people' }
      },
      {
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/customers/Detail.vue'),
        meta: { title: '客户详情', hidden: true }
      },
      {
        path: 'loans',
        name: 'Loans',
        component: () => import('@/views/loans/List.vue'),
        meta: { title: '贷款申请', icon: 'file-text' }
      },
      {
        path: 'loans/:id',
        name: 'LoanDetail',
        component: () => import('@/views/loans/Detail.vue'),
        meta: { title: '贷款详情', hidden: true }
      },
      {
        path: 'risk/rules',
        name: 'RiskRules',
        component: () => import('@/views/risk/Rules.vue'),
        meta: { title: '风控规则', icon: 'settings', group: '风控管理' }
      },
      {
        path: 'risk/blacklist',
        name: 'Blacklist',
        component: () => import('@/views/risk/Blacklist.vue'),
        meta: { title: '黑名单管理', icon: 'ban', group: '风控管理' }
      },
      {
        path: 'risk/credit-reports',
        name: 'CreditReports',
        component: () => import('@/views/risk/CreditReports.vue'),
        meta: { title: '信用报告', icon: 'document', group: '风控管理' }
      },
      {
        path: 'system/users',
        name: 'Users',
        component: () => import('@/views/system/Users.vue'),
        meta: { title: '用户管理', icon: 'person', group: '系统管理', roles: ['admin', 'manager'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  document.title = to.meta.title ? `${to.meta.title} - 金盾信贷风控审批系统` : '金盾信贷风控审批系统'

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next({ path: '/dashboard' })
  } else if (to.meta.roles && userStore.userInfo) {
    if (!to.meta.roles.includes(userStore.userInfo.role)) {
      next({ path: '/dashboard' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
