<template>
  <div class="app-container">
    <div class="header">
      <div class="logo-area">
        <el-icon class="logo-icon" :size="28"><DataAnalysis /></el-icon>
        <span class="title">AI 供应链风控大脑 <span class="version">PRO</span></span>
      </div>
      <div class="status-bar">
        <span class="time">{{ currentTime }}</span>
        <el-tag type="success" effect="dark" round>系统在线</el-tag>
      </div>
    </div>

    <div class="search-section">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="请输入企业名称（如：腾讯控股、比亚迪、特斯拉）"
          class="custom-input"
          size="large"
          @keyup.enter="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" size="large" @click="handleSearch" :loading="loading" class="search-btn">
          全维评估
        </el-button>
      </div>
    </div>

    <div v-if="result" class="dashboard animate__animated animate__fadeIn">

      <el-row :gutter="20">
        <el-col :span="6">
          <div class="panel score-panel">
            <div class="panel-title">综合信用评分</div>
            <div class="score-chart">
              <div class="score-ring" :class="getScoreClass(result.risk_data.score)">
                <span class="score-val">{{ result.risk_data.score }}</span>
                <span class="score-label">{{ result.risk_data.level }}级</span>
              </div>
            </div>
            <div class="company-badges">
              <el-tag effect="plain" type="info">{{ result.legal }}</el-tag>
              <el-tag effect="plain" type="primary">{{ result.capital }}</el-tag>
            </div>
          </div>
        </el-col>

        <el-col :span="10">
          <div class="panel market-panel">
            <div class="panel-title">实时行情监测 (Real-time)</div>
            <div class="market-grid">
              <div class="market-item">
                <div class="m-label">当前股价</div>
                <div class="m-val highlight">{{ result.stock_info.price }}</div>
              </div>
              <div class="market-item">
                <div class="m-label">市盈率(PE)</div>
                <div class="m-val">{{ result.stock_info.pe }}</div>
              </div>
              <div class="market-item">
                <div class="m-label">波动率 (风险)</div>
                <div class="m-val danger">{{ result.stock_info.volatility }}</div>
              </div>
              <div class="market-item">
                <div class="m-label">市场趋势</div>
                <div class="m-val" :class="isPositive(result.stock_info.trend) ? 'up' : 'down'">
                  {{ result.stock_info.trend }}
                </div>
              </div>
            </div>
            <div class="market-desc">
              <el-alert :title="'基于 ' + result.stock_info.volatility + ' 的波动率分析，该企业供应链外部风险敞口' + (parseFloat(result.stock_info.volatility) > 5 ? '较大' : '可控') + '。'" type="info" :closable="false" show-icon />
            </div>
          </div>
        </el-col>

        <el-col :span="8">
          <div class="panel ai-panel">
            <div class="panel-title">
              <span>DeepSeek 深度研报</span>
              <el-icon class="ai-icon"><Cpu /></el-icon>
            </div>
            <div class="ai-content-box">
              <p class="ai-text">{{ result.ai_analysis }}</p>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="chart-row">
        <el-col :span="8">
          <div class="panel chart-panel">
            <div class="panel-title">供应链韧性雷达</div>
            <div id="radarChart" class="chart-container"></div>
          </div>
        </el-col>

        <el-col :span="16">
          <div class="panel chart-panel">
            <div class="panel-title">全球节点流量与成本分析</div>
            <div id="barChart" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>

      <div class="metrics-row">
        <div class="metric-card">
          <div class="icon-bg blue"><el-icon><Goods /></el-icon></div>
          <div class="metric-info">
            <div class="num">{{ result.risk_data.stats.supplier_nodes }}</div>
            <div class="txt">核心供应商</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="icon-bg green"><el-icon><Van /></el-icon></div>
          <div class="metric-info">
            <div class="num">{{ result.risk_data.stats.logistics_routes }}</div>
            <div class="txt">物流专线</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="icon-bg orange"><el-icon><House /></el-icon></div>
          <div class="metric-info">
            <div class="num">{{ result.risk_data.stats.warehouses }}</div>
            <div class="txt">仓储中心</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="icon-bg purple"><el-icon><Timer /></el-icon></div>
          <div class="metric-info">
            <div class="num">{{ result.risk_data.stats.transport_efficiency }}</div>
            <div class="txt">周转效率</div>
          </div>
        </div>
      </div>

      <div class="panel table-panel">
        <div class="panel-title">节点监控详情</div>
        <el-table :data="result.risk_data.nodes_list" style="width: 100%" :row-class-name="tableRowClassName">
          <el-table-column prop="name" label="节点名称" />
          <el-table-column prop="status" label="运行状态">
            <template #default="scope">
              <el-tag size="small" :type="scope.row.status === '正常' ? 'success' : 'danger'" effect="dark">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="flow" label="吞吐流量 (吨)" />
          <el-table-column prop="cost" label="运营成本 (万美元)" />
          <el-table-column prop="efficiency" label="效率">
             <template #default="scope">
               <el-progress :percentage="parseInt(scope.row.efficiency)" :color="customColors" />
             </template>
          </el-table-column>
        </el-table>
      </div>

    </div>

    <div v-else class="empty-holder">
      <div class="empty-box">
        <el-icon class="empty-icon"><DataLine /></el-icon>
        <p>请输入上市企业名称，启动全维风控模型</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const searchQuery = ref('')
const loading = ref(false)
const result = ref(null)
const currentTime = ref('')

// 更新时间
setInterval(() => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString()
}, 1000)

const customColors = [
  { color: '#f56c6c', percentage: 60 },
  { color: '#e6a23c', percentage: 80 },
  { color: '#5cb87a', percentage: 100 },
]

// 核心搜索逻辑
const handleSearch = async () => {
  if (!searchQuery.value) return
  loading.value = true
  result.value = null // 清空旧数据

  try {
    const response = await axios.post('http://127.0.0.1:8080/assess', {
      company_name: searchQuery.value
    })

    if (response.data.status === 'success') {
      result.value = response.data
      ElMessage.success('分析完成')

      // 等待 DOM 更新后渲染图表
      await nextTick()
      initCharts()
    } else {
      ElMessage.warning(response.data.message || '未查询到数据')
    }
  } catch (error) {
    ElMessage.error('连接服务器失败')
  } finally {
    loading.value = false
  }
}

// 初始化 ECharts 图表
const initCharts = () => {
  if (!result.value) return

  // 1. 雷达图
  const radarChart = echarts.init(document.getElementById('radarChart'))
  const dims = result.value.risk_data.dimensions
  const radarOption = {
    backgroundColor: 'transparent',
    tooltip: {},
    radar: {
      indicator: [
        { name: '供应稳定性', max: 100 },
        { name: '链条多样性', max: 100 },
        { name: '物流可靠性', max: 100 },
        { name: '仓储效率', max: 100 }
      ],
      splitArea: {
        areaStyle: {
          color: ['rgba(64,158,255,0.1)', 'rgba(64,158,255,0.2)']
        }
      },
      axisName: { color: '#fff' }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          dims.supplier_stability.score,
          dims.chain_diversity.score,
          dims.logistics_reliability.score,
          dims.warehouse_efficiency.score
        ],
        name: '供应链能力',
        areaStyle: { color: 'rgba(64, 158, 255, 0.5)' },
        lineStyle: { color: '#409eff' }
      }]
    }]
  }
  radarChart.setOption(radarOption)

  // 2. 柱状图 (流量 vs 成本)
  const barChart = echarts.init(document.getElementById('barChart'))
  const nodes = result.value.risk_data.nodes_list
  const barOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#fff' }, bottom: 0 },
    grid: { top: '15%', bottom: '20%', left: '5%', right: '5%', containLabel: true },
    xAxis: {
      type: 'category',
      data: nodes.map(n => n.name.split('-')[1]), // 取地区名
      axisLabel: { color: '#ccc' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#ccc' }
    },
    series: [
      {
        name: '吞吐流量',
        type: 'bar',
        data: nodes.map(n => parseInt(n.flow.replace(/,/g, ''))),
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: '#00f2fe'}, {offset: 1, color: '#4facfe'}]) }
      },
      {
        name: '运营成本',
        type: 'line',
        data: nodes.map(n => parseInt(n.cost)),
        itemStyle: { color: '#f6d365' },
        lineStyle: { width: 3 }
      }
    ]
  }
  barChart.setOption(barOption)

  // 窗口缩放自适应
  window.addEventListener('resize', () => {
    radarChart.resize()
    barChart.resize()
  })
}

// 辅助函数
const isPositive = (str) => str && !str.includes('-')
const getScoreClass = (score) => {
  if (score >= 85) return 'ring-aaa'
  if (score >= 70) return 'ring-aa'
  return 'ring-b'
}
const tableRowClassName = ({ rowIndex }) => rowIndex % 2 === 1 ? 'row-dark' : ''
</script>

<style scoped>
/* 整体布局 - 深空灰背景 */
.app-container {
  min-height: 100vh;
  background-color: #0b1120;
  color: #fff;
  padding: 20px 40px;
  font-family: 'PingFang SC', sans-serif;
}

/* 顶部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 1px solid #1e293b;
  padding-bottom: 15px;
}
.logo-area { display: flex; align-items: center; gap: 10px; color: #38bdf8; }
.title { font-size: 24px; font-weight: bold; }
.version { font-size: 12px; background: #38bdf8; color: #000; padding: 2px 6px; border-radius: 4px; vertical-align: super;}
.status-bar { display: flex; gap: 15px; align-items: center; }

/* 搜索框 */
.search-section { display: flex; justify-content: center; margin-bottom: 30px; }
.search-box { width: 600px; display: flex; gap: 10px; }
.custom-input :deep(.el-input__wrapper) { background-color: #1e293b; box-shadow: none; border: 1px solid #334155; }
.custom-input :deep(.el-input__inner) { color: white; }

/* 通用面板样式 */
.panel {
  background: #151e32;
  border: 1px solid #2a3b55;
  border-radius: 8px;
  padding: 15px;
  height: 100%;
  box-sizing: border-box;
}
.panel-title { font-size: 14px; color: #94a3b8; margin-bottom: 15px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase;}

/* 1. 评分面板 */
.score-panel { text-align: center; height: 260px; }
.score-ring {
  width: 120px; height: 120px; border-radius: 50%; border: 8px solid; margin: 20px auto;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  box-shadow: 0 0 15px rgba(0,0,0,0.5);
}
.score-val { font-size: 32px; font-weight: bold; }
.score-label { font-size: 12px; opacity: 0.8; }
.ring-aaa { border-color: #10b981; color: #10b981; }
.ring-aa { border-color: #3b82f6; color: #3b82f6; }
.ring-b { border-color: #f59e0b; color: #f59e0b; }
.company-badges { display: flex; justify-content: center; gap: 10px; margin-top: 15px; }

/* 2. 行情面板 */
.market-panel { height: 260px; }
.market-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }
.market-item { background: #1e293b; padding: 10px; border-radius: 6px; text-align: center; }
.m-label { font-size: 12px; color: #64748b; margin-bottom: 5px; }
.m-val { font-size: 18px; font-weight: bold; }
.highlight { color: #facc15; }
.danger { color: #f43f5e; }
.up { color: #ef4444; } /* A股红涨 */
.down { color: #22c55e; } /* A股绿跌 */

/* 3. AI 面板 */
.ai-panel { height: 260px; overflow: hidden; display: flex; flex-direction: column; }
.ai-icon { float: right; color: #8b5cf6; font-size: 18px; }
.ai-content-box {
  background: #0f172a; flex: 1; padding: 10px; border-radius: 6px;
  overflow-y: auto; font-size: 13px; line-height: 1.6; color: #cbd5e1;
  border-left: 3px solid #8b5cf6;
}

/* 图表区 */
.chart-row { margin-top: 20px; }
.chart-panel { height: 320px; }
.chart-container { width: 100%; height: 280px; }

/* 指标卡片 */
.metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
.metric-card {
  background: #151e32; border: 1px solid #2a3b55; border-radius: 8px; padding: 15px;
  display: flex; align-items: center; gap: 15px; transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-3px); border-color: #38bdf8; }
.icon-bg { width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: white;}
.blue { background: #3b82f6; } .green { background: #10b981; } .orange { background: #f59e0b; } .purple { background: #8b5cf6; }
.num { font-size: 22px; font-weight: bold; }
.txt { font-size: 12px; color: #94a3b8; }

/* 表格 */
.table-panel { margin-top: 20px; }
:deep(.el-table) { background: transparent; --el-table-tr-bg-color: transparent; --el-table-header-bg-color: #1e293b; color: #fff; --el-table-border-color: #2a3b55; }
:deep(.row-dark) { background: #111827; }

/* 空状态 */
.empty-holder { display: flex; justify-content: center; margin-top: 100px; color: #475569; }
.empty-box { text-align: center; }
.empty-icon { font-size: 80px; margin-bottom: 20px; opacity: 0.5; }
</style>