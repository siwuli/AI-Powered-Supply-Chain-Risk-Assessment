<template>
  <div class="app-container">
    <div class="header">
      <div class="logo-area">
        <span class="logo-icon">🔗</span>
        <span class="title">AI 供应链风控大脑</span>
      </div>
      <div class="status-tags">
        <el-tag type="success" effect="dark" round>系统运行中</el-tag>
        <el-tag type="info" effect="plain" round>数据源：AkShare + DeepSeek</el-tag>
      </div>
    </div>

    <div class="search-section">
      <div class="search-wrapper">
        <el-input
          v-model="searchQuery"
          placeholder="请输入企业名称（推荐：宁德时代、比亚迪、上汽集团、顺丰控股）"
          class="custom-search"
          size="large"
          @keyup.enter="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" size="large" @click="handleSearch" :loading="loading" class="search-btn">
          立即评估
        </el-button>
      </div>
    </div>

    <div v-if="result" class="dashboard animate__animated animate__fadeIn">

      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="box-card score-card">
            <template #header>
              <div class="card-header">
                <span><el-icon><Odometer /></el-icon> 供应链信用评分</span>
              </div>
            </template>
            <div class="score-body">
              <div class="score-circle" :class="getScoreClass(result.risk_data.score)">
                <span class="score-num">{{ result.risk_data.score }}</span>
                <span class="score-level">{{ result.risk_data.level }}级</span>
              </div>
              <div class="market-info">
                <div class="info-item">
                  <div class="label">股价波动率</div>
                  <div class="val danger">{{ result.stock_info.volatility }}</div>
                </div>
                <div class="info-item">
                  <div class="label">市场趋势</div>
                  <div class="val" :class="isPositive(result.stock_info.trend) ? 'success' : 'danger'">
                    {{ result.stock_info.trend }}
                  </div>
                </div>
              </div>
              <div class="company-tags">
                <el-tag>{{ result.industry }}</el-tag>
                <el-tag type="info">{{ result.legal }}</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card class="box-card ai-card">
            <template #header>
              <div class="card-header ai-header">
                <span class="ai-title"><el-icon><Cpu /></el-icon> DeepSeek 深度风控报告</span>
                <el-tag effect="dark" color="#626aef" style="border:none">AI Generated</el-tag>
              </div>
            </template>
            <div class="ai-content">
              <p class="ai-text">{{ result.ai_analysis }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <div class="metrics-row">
        <el-row :gutter="15">
          <el-col :span="6">
            <div class="metric-box blue-box">
              <div class="metric-num">{{ result.risk_data.stats.supplier_nodes }}</div>
              <div class="metric-label">供应商节点</div>
              <el-progress :percentage="80" :show-text="false" stroke-width="4" color="rgba(255,255,255,0.5)"/>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-box green-box">
              <div class="metric-num">{{ result.risk_data.stats.logistics_routes }}</div>
              <div class="metric-label">活跃物流路线</div>
              <el-progress :percentage="65" :show-text="false" stroke-width="4" color="rgba(255,255,255,0.5)"/>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-box orange-box">
              <div class="metric-num">{{ result.risk_data.stats.warehouses }}</div>
              <div class="metric-label">仓储中心</div>
              <el-progress :percentage="40" :show-text="false" stroke-width="4" color="rgba(255,255,255,0.5)"/>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-box purple-box">
              <div class="metric-num">{{ result.risk_data.stats.transport_efficiency }}</div>
              <div class="metric-label">全链运输效率</div>
              <el-progress :percentage="parseInt(result.risk_data.stats.transport_efficiency)" :show-text="false" stroke-width="4" color="rgba(255,255,255,0.5)"/>
            </div>
          </el-col>
        </el-row>
      </div>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span><el-icon><Share /></el-icon> 关键供应链节点监控</span>
              </div>
            </template>
            <el-table :data="result.risk_data.nodes_list" style="width: 100%" :row-class-name="tableRowClassName">
              <el-table-column prop="name" label="节点名称" width="180">
                <template #default="scope">
                  <div style="font-weight:bold">{{ scope.row.name }}</div>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.status === '正常' ? 'success' : 'danger'" effect="dark">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="flow" label="实时流量" />
              <el-table-column prop="efficiency" label="节点效率" />
              <el-table-column prop="cost" label="物流成本" />
              <el-table-column prop="risk" label="风险系数">
                <template #default="scope">
                  <span :style="{color: parseInt(scope.row.risk) > 20 ? '#f56c6c' : '#67c23a'}">
                    {{ scope.row.risk }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

    </div>

    <div v-else class="empty-state">
      <el-empty description="请输入 A股 上市企业名称，启动 AI 风控引擎" image-size="200"></el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const searchQuery = ref('')
const loading = ref(false)
const result = ref(null)

const handleSearch = async () => {
  if (!searchQuery.value) return

  loading.value = true
  result.value = null // 重置数据

  try {
    // 调用后端接口
    const response = await axios.post('http://127.0.0.1:8080/assess', {
      company_name: searchQuery.value
    })

    if (response.data.status === 'success') {
      result.value = response.data
      ElMessage.success('评估完成')
    } else {
      ElMessage.warning(response.data.message || '未查询到相关数据')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('连接后端失败，请确保 backend/main.py 已运行')
  } finally {
    loading.value = false
  }
}

// 辅助函数：判断涨跌
const isPositive = (str) => {
  return str && !str.includes('-')
}

// 辅助函数：评分颜色
const getScoreClass = (score) => {
  if (score >= 85) return 'score-aaa'
  if (score >= 70) return 'score-aa'
  return 'score-b'
}

// 表格隔行变色
const tableRowClassName = ({ rowIndex }) => {
  return rowIndex % 2 === 1 ? 'warning-row' : ''
}
</script>

<style scoped>
/* 全局布局 */
.app-container {
  min-height: 100vh;
  background-color: #0f172a; /* 深邃蓝黑背景 */
  color: #fff;
  padding: 20px 40px;
  font-family: 'Inter', 'Helvetica Neue', sans-serif;
}

/* 头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  border-bottom: 1px solid #1e293b;
  padding-bottom: 20px;
}
.logo-area {
  display: flex;
  align-items: center;
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(to right, #409eff, #67c23a);
  -webkit-background-clip: text;
  color: transparent;
}
.logo-icon { margin-right: 10px; filter: grayscale(0); }

/* 搜索区 */
.search-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}
.search-wrapper {
  display: flex;
  width: 60%;
  gap: 10px;
}
.custom-search :deep(.el-input__wrapper) {
  background-color: #1e293b;
  box-shadow: none;
  border: 1px solid #334155;
}
.custom-search :deep(.el-input__inner) {
  color: white;
}

/* 卡片通用样式 */
.box-card {
  background-color: #1e293b !important;
  border: 1px solid #334155 !important;
  color: white !important;
  border-radius: 12px;
}
.card-header {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

/* 评分卡片 */
.score-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}
.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 8px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 0 20px rgba(0,0,0,0.5);
}
.score-num { font-size: 36px; font-weight: bold; }
.score-level { font-size: 14px; opacity: 0.8; }
.score-aaa { border-color: #67c23a; color: #67c23a; }
.score-aa { border-color: #409eff; color: #409eff; }
.score-b { border-color: #e6a23c; color: #e6a23c; }

.market-info {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}
.info-item { text-align: center; }
.label { font-size: 12px; color: #94a3b8; }
.val { font-size: 16px; font-weight: bold; }
.val.danger { color: #f56c6c; }
.val.success { color: #67c23a; }

/* AI 报告卡片 */
.ai-card {
  height: 100%;
}
.ai-header { justify-content: space-between; width: 100%; }
.ai-content {
  background-color: #0f172a;
  padding: 15px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.8;
  color: #cbd5e1;
  min-height: 200px;
  border-left: 3px solid #626aef;
}
.ai-text { white-space: pre-wrap; }

/* 核心指标色块 */
.metrics-row { margin-top: 20px; }
.metric-box {
  padding: 20px;
  border-radius: 12px;
  color: white;
  text-align: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}
.metric-box:hover { transform: translateY(-5px); }
.metric-num { font-size: 28px; font-weight: 800; margin-bottom: 5px; }
.metric-label { font-size: 12px; opacity: 0.8; margin-bottom: 15px; }
.blue-box { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
.green-box { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.orange-box { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.purple-box { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }

/* 表格调整 */
:deep(.el-table) {
  background-color: transparent !important;
  color: #fff !important;
  --el-table-border-color: #334155;
  --el-table-header-bg-color: #1e293b;
  --el-table-row-hover-bg-color: #334155;
  --el-table-tr-bg-color: transparent;
}
:deep(.el-table th), :deep(.el-table tr) {
  background-color: transparent !important;
}
</style>