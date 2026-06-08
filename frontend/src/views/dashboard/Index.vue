<template>
  <div class="page-container">
    <n-row :gutter="20">
      <n-col :span="6" v-for="(card, index) in statCards" :key="index">
        <n-card class="stat-card" :bordered="false">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">{{ card.label }}</p>
              <p class="stat-value">{{ card.value }}</p>
              <p class="stat-desc" :style="{ color: card.color }">{{ card.desc }}</p>
            </div>
            <div class="stat-icon" :style="{ background: card.bgColor }">
              <n-icon :component="card.icon" :size="28" :style="{ color: card.color }" />
            </div>
          </div>
        </n-card>
      </n-col>
    </n-row>

    <n-row :gutter="20" style="margin-top: 20px">
      <n-col :span="16">
        <n-card title="申请趋势" :bordered="false" class="chart-card">
          <v-chart class="chart" :option="trendChartOption" autoresize />
        </n-card>
      </n-col>
      <n-col :span="8">
        <n-card title="风险分布" :bordered="false" class="chart-card">
          <v-chart class="chart" :option="riskChartOption" autoresize />
        </n-card>
      </n-col>
    </n-row>

    <n-row :gutter="20" style="margin-top: 20px">
      <n-col :span="12">
        <n-card title="贷款类型分布" :bordered="false" class="chart-card">
          <v-chart class="chart" :option="loanTypeChartOption" autoresize />
        </n-card>
      </n-col>
      <n-col :span="12">
        <n-card title="审批通过率" :bordered="false" class="chart-card">
          <div class="rate-container">
            <n-progress
              type="circle"
              :percentage="stats.pass_rate || 0"
              :stroke-width="12"
              :indicator-text-color="'#18a058'"
              :color="'#18a058'"
              :rail-color="'#e5e7eb'"
              style="width: 200px; height: 200px"
            >
              {{ stats.pass_rate || 0 }}%
            </n-progress>
            <div class="rate-info">
              <div class="rate-item">
                <span class="rate-label">通过数</span>
                <span class="rate-value success">{{ stats.approved_count || 0 }}</span>
              </div>
              <div class="rate-item">
                <span class="rate-label">拒绝数</span>
                <span class="rate-value danger">{{ stats.rejected_count || 0 }}</span>
              </div>
              <div class="rate-item">
                <span class="rate-label">待处理</span>
                <span class="rate-value warning">{{ stats.pending_count || 0 }}</span>
              </div>
            </div>
          </div>
        </n-card>
      </n-col>
    </n-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, h } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import {
  FileTrayFull,
  CheckmarkCircle,
  CloseCircle,
  Alert,
  Time,
  Cash,
  People
} from '@vicons/ionicons5'
import {
  getDashboardStats,
  getTrendData,
  getLoanTypeDistribution
} from '@/api/risk'
import { formatMoney } from '@/utils'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const stats = ref({})
const trendData = ref([])
const loanTypeData = ref([])

const statCards = computed(() => [
  {
    label: '申请总数',
    value: stats.value.total_applications || 0,
    desc: `今日新增 ${stats.value.today_applications || 0} 笔`,
    icon: FileTrayFull,
    color: '#3b82f6',
    bgColor: 'rgba(59, 130, 246, 0.1)'
  },
  {
    label: '审批通过',
    value: stats.value.approved_count || 0,
    desc: `金额 ${formatMoney(stats.value.approved_amount)} 元`,
    icon: CheckmarkCircle,
    color: '#18a058',
    bgColor: 'rgba(24, 160, 88, 0.1)'
  },
  {
    label: '待处理',
    value: stats.value.pending_count || 0,
    desc: '需要人工审核',
    icon: Time,
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.1)'
  },
  {
    label: '黑名单',
    value: stats.value.blacklist_count || 0,
    desc: '高风险客户',
    icon: Alert,
    color: '#dc2626',
    bgColor: 'rgba(220, 38, 38, 0.1)'
  }
])

const trendChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['申请数', '通过数', '拒绝数']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: trendData.value.map(item => item.date)
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '申请数',
      type: 'line',
      smooth: true,
      data: trendData.value.map(item => item.application_count),
      lineStyle: { color: '#3b82f6', width: 2 },
      itemStyle: { color: '#3b82f6' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
          ]
        }
      }
    },
    {
      name: '通过数',
      type: 'line',
      smooth: true,
      data: trendData.value.map(item => item.approved_count),
      lineStyle: { color: '#18a058', width: 2 },
      itemStyle: { color: '#18a058' }
    },
    {
      name: '拒绝数',
      type: 'line',
      smooth: true,
      data: trendData.value.map(item => item.rejected_count),
      lineStyle: { color: '#dc2626', width: 2 },
      itemStyle: { color: '#dc2626' }
    }
  ]
}))

const riskChartOption = computed(() => {
  const dist = stats.value.risk_distribution || {}
  return {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center'
    },
    series: [
      {
        name: '风险等级',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        data: [
          { value: dist.low || 0, name: '低风险', itemStyle: { color: '#18a058' } },
          { value: dist.medium_low || 0, name: '中低风险', itemStyle: { color: '#047857' } },
          { value: dist.medium || 0, name: '中风险', itemStyle: { color: '#f59e0b' } },
          { value: dist.medium_high || 0, name: '中高风险', itemStyle: { color: '#ea580c' } },
          { value: dist.high || 0, name: '高风险', itemStyle: { color: '#dc2626' } },
          { value: dist.extreme_high || 0, name: '极高风险', itemStyle: { color: '#991b1b' } }
        ]
      }
    ]
  }
})

const loanTypeChartOption = computed(() => {
  const typeMap = {
    personal: '个人贷款',
    business: '企业贷款',
    mortgage: '抵押贷款',
    car: '车贷',
    consumer: '消费贷款'
  }
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: loanTypeData.value.map(item => typeMap[item.loan_type] || item.loan_type)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '申请笔数',
        type: 'bar',
        data: loanTypeData.value.map(item => item.count),
        itemStyle: {
          color: '#3b82f6',
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '40%'
      }
    ]
  }
})

async function fetchData() {
  try {
    const [statsRes, trendRes, typeRes] = await Promise.all([
      getDashboardStats(),
      getTrendData(15),
      getLoanTypeDistribution()
    ])
    stats.value = statsRes.data
    trendData.value = trendRes.data
    loanTypeData.value = typeRes.data
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.stat-card {
  border-radius: 12px;

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    .stat-label {
      font-size: 14px;
      color: #64748b;
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 8px;
    }

    .stat-desc {
      font-size: 12px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.chart-card {
  border-radius: 12px;

  .chart {
    height: 300px;
  }
}

.rate-container {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 20px 0;

  .rate-info {
    display: flex;
    flex-direction: column;
    gap: 20px;

    .rate-item {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .rate-label {
        font-size: 14px;
        color: #64748b;
      }

      .rate-value {
        font-size: 24px;
        font-weight: 600;

        &.success { color: #18a058; }
        &.danger { color: #dc2626; }
        &.warning { color: #f59e0b; }
      }
    }
  }
}
</style>
