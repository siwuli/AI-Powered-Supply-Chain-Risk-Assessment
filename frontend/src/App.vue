<template>
  <div class="app-container">
    <div class="header">
      <div class="logo-area">
        <el-icon class="logo-icon" :size="28"><DataAnalysis /></el-icon>
        <span class="title">AI + 供应链金融 大数据风控评分卡</span>
      </div>
      <div class="status-bar">
        <el-tooltip content="数据源：东方财富 Real-time API" placement="bottom">
          <el-tag type="warning" effect="dark" round class="source-tag">
            <el-icon><Coin /></el-icon> 实时行情数据
          </el-tag>
        </el-tooltip>
        <el-tooltip content="推理引擎：DeepSeek V3" placement="bottom">
          <el-tag type="info" color="#626aef" effect="dark" round class="source-tag" style="border:none">
            <el-icon><Cpu /></el-icon> AI 驱动
          </el-tag>
        </el-tooltip>
        <span class="time">{{ currentTime }}</span>
      </div>
    </div>

    <div class="search-section">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="请输入企业名称（如：腾讯控股、比亚迪、顺丰控股）"
          class="custom-input" size="large" @keyup.enter="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" size="large" @click="handleSearch" :loading="loading" class="search-btn">
          开始深度评估
        </el-button>
      </div>
    </div>

    <div v-if="result" class="dashboard animate__animated animate__fadeIn">

      <el-row :gutter="20" class="top-row">
        <el-col :span="6">
          <div class="panel score-panel">
            <div class="panel-title">综合信用评分</div>
            <div class="score-ring" :class="getScoreClass(result.base.score)">
              <span class="score-val">{{ result.base.score }}</span>
              <span class="score-lvl">{{ result.base.level }}级</span>
            </div>
            <div class="score-badges">
              <el-tag effect="dark" type="success">数据质量优秀</el-tag>
            </div>
          </div>
        </el-col>
        <el-col :span="10">
          <div class="panel market-panel">
            <div class="panel-title">实时风控监测</div>
            <div class="market-grid-top">
              <div class="m-item">
                <div class="m-lbl">当前股价</div>
                <div class="m-v highlight">{{ result.stock.price }}</div>
              </div>
              <div class="m-item">
                <div class="m-lbl">波动率 (风险)</div>
                <div class="m-v danger">{{ result.stock.vol }}</div>
              </div>
              <div class="m-item">
                <div class="m-lbl">市场趋势</div>
                <div class="m-v" :class="isPositive(result.stock.trend)?'up':'down'">{{ result.stock.trend }}</div>
              </div>
              <div class="m-item">
                <div class="m-lbl">市盈率</div>
                <div class="m-v">{{ result.stock.pe }}</div>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="panel ai-panel">
            <div class="panel-title">
              <span>DeepSeek 深度研报</span>
              <el-icon color="#8b5cf6"><Cpu /></el-icon>
            </div>
            <div class="ai-box">
              {{ result.ai_analysis }}
            </div>
          </div>
        </el-col>
      </el-row>

      <div class="section-divider">核心财务指标 (Core Financials)</div>
      <div class="core-grid">
        <div class="c-card bg-blue">
          <div class="cv">{{ result.data.financial.core.price }}</div><div class="cl">股价</div>
        </div>
        <div class="c-card bg-green">
          <div class="cv">{{ result.data.financial.core.mv }}</div><div class="cl">市值</div>
        </div>
        <div class="c-card bg-orange">
          <div class="cv">{{ result.data.financial.core.pe }}</div><div class="cl">市盈率</div>
        </div>
        <div class="c-card bg-purple">
          <div class="cv">{{ result.data.financial.core.revenue }}</div><div class="cl">营收</div>
        </div>
        <div class="c-card bg-dark">
          <div class="cv small">{{ result.data.financial.core.volume }}</div><div class="cl">成交量</div>
        </div>
        <div class="c-card bg-dark">
          <div class="cv small">{{ result.data.financial.core.high }}</div><div class="cl">最高价</div>
        </div>
        <div class="c-card bg-dark">
          <div class="cv small">{{ result.data.financial.core.low }}</div><div class="cl">最低价</div>
        </div>
      </div>

      <el-row :gutter="20" style="margin-top:20px;">
        <el-col :span="6">
          <div class="panel mini-panel">
            <div class="p-head"><el-icon><TrendCharts /></el-icon> 估值分析</div>
            <div class="d-grid"><div class="d-i"><span>市净率</span><b>{{result.data.financial.deep.valuation.pb}}</b></div><div class="d-i"><span>股息率</span><b>{{result.data.financial.deep.valuation.div}}</b></div></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="panel mini-panel">
            <div class="p-head"><el-icon><Top /></el-icon> 成长性分析</div>
            <div class="d-grid"><div class="d-i"><span>营收增长</span><b>{{result.data.financial.deep.growth.rev}}</b></div><div class="d-i"><span>EPS增长</span><b>{{result.data.financial.deep.growth.eps}}</b></div></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="panel mini-panel">
            <div class="p-head"><el-icon><FirstAidKit /></el-icon> 财务健康度</div>
            <div class="d-grid"><div class="d-i"><span>流动比率</span><b>{{result.data.financial.deep.health.cur}}</b></div><div class="d-i"><span>利息覆盖</span><b>{{result.data.financial.deep.health.int}}</b></div></div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="panel mini-panel">
            <div class="p-head"><el-icon><Warning /></el-icon> 风险评估</div>
            <div class="d-grid"><div class="d-i danger"><span>波动率</span><b>{{result.data.financial.deep.risk.vol}}</b></div><div class="d-i"><span>回撤</span><b>{{result.data.financial.deep.risk.drawdown}}</b></div></div>
          </div>
        </el-col>
      </el-row>

      <div class="section-divider">供应链运营分析 (Operations)</div>
      <el-row :gutter="20">
        <el-col :span="6"><div class="m-box b-blue"><div class="mn">{{result.data.logistics.stats.supplier_nodes}}</div><div class="mt">供应商节点</div></div></el-col>
        <el-col :span="6"><div class="m-box b-green"><div class="mn">{{result.data.logistics.stats.logistics_routes}}</div><div class="mt">物流路线</div></div></el-col>
        <el-col :span="6"><div class="m-box b-orange"><div class="mn">{{result.data.logistics.stats.warehouses}}</div><div class="mt">仓储中心</div></div></el-col>
        <el-col :span="6"><div class="m-box b-purple"><div class="mn">{{result.data.logistics.stats.transport_efficiency}}</div><div class="mt">运输效率</div></div></el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top:20px;">
        <el-col :span="12">
          <div class="risk-card warning-border">
            <div class="rc-head warn-bg"><el-icon><WarnTriangleFilled /></el-icon> 风险识别与预警</div>
            <div class="rc-body">
              <div v-for="(w,i) in result.data.logistics.warnings" :key="i" class="risk-row">
                <el-tag :type="w.type==='high'?'danger':w.type==='medium'?'warning':'info'" size="small">{{w.title}}</el-tag>
                <span>{{w.desc}}</span>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="risk-card success-border">
            <div class="rc-head success-bg"><el-icon><Opportunity /></el-icon> 改进建议</div>
            <div class="rc-body">
              <div v-for="(s,i) in result.data.logistics.suggestions" :key="i" class="sug-row">
                <el-icon color="#67c23a"><CircleCheckFilled /></el-icon> {{s}}
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <div class="panel adv-panel">
        <div class="adv-i"><span>总运营成本</span><b>{{result.data.logistics.advanced.total_cost}}</b></div>
        <div class="adv-i"><span>平均交付时间</span><b>{{result.data.logistics.advanced.avg_delivery_time}}</b></div>
        <div class="adv-i"><span>准时交付率</span><b class="ok">{{result.data.logistics.advanced.on_time_rate}}</b></div>
        <div class="adv-i"><span>节点健康率</span><b class="ok">{{result.data.logistics.advanced.node_health}}</b></div>
      </div>

    </div>

    <div class="footer">
      <div class="f-content">
        <div class="f-col"><h4>产品功能</h4><a>风控评估</a><a>实时监控</a><a>决策设置</a></div>
        <div class="f-col"><h4>快速链接</h4><a>关于我们</a><a>隐私政策</a><a>服务条款</a></div>
        <div class="f-col"><h4>联系方式</h4>
          <span><el-icon><Location /></el-icon> 苏州工业园区职业技术学院</span>
          <span><el-icon><Phone /></el-icon> 13626192149</span>
          <span><el-icon><Message /></el-icon> 1954129550@qq.com</span>
        </div>
      </div>
      <div class="copyright">© 2026 智链风控. 保留所有权利</div>
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
const currentTime = ref(new Date().toLocaleTimeString())
setInterval(() => { currentTime.value = new Date().toLocaleTimeString() }, 1000)

const handleSearch = async () => {
  if (!searchQuery.value) return
  loading.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8080/assess', { company_name: searchQuery.value })
    if (res.data.status === 'success') {
      result.value = res.data
      ElMessage.success('分析完成')
    } else { ElMessage.warning(res.data.message) }
  } catch(e) { ElMessage.error('连接失败') } finally { loading.value = false }
}

const isPositive = (s) => s && !s.includes('-')
const getScoreClass = (s) => s >= 80 ? 'sc-a' : s >= 60 ? 'sc-b' : 'sc-c'
</script>

<style scoped>
.app-container { min-height: 100vh; background: #0b1120; color: #fff; padding: 20px 40px 0; font-family: sans-serif; display: flex; flex-direction: column; }
.header { display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-bottom: 20px; }
.logo-area { color: #38bdf8; font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 10px; }
.status-bar { display: flex; gap: 10px; align-items: center; }
.search-section { display: flex; justify-content: center; margin-bottom: 20px; }
.search-box { width: 600px; display: flex; gap: 10px; }
.custom-input :deep(.el-input__inner) { color: #fff; background: #1e293b; }

.panel { background: #151e32; border: 1px solid #2a3b55; border-radius: 8px; padding: 15px; height: 100%; box-sizing: border-box; }
.panel-title { color: #94a3b8; font-weight: bold; margin-bottom: 15px; display: flex; justify-content: space-between; }

/* 评分环 */
.score-panel { text-align: center; height: 240px; }
.score-ring { width: 100px; height: 100px; border-radius: 50%; border: 8px solid; margin: 10px auto; display: flex; flex-direction: column; justify-content: center; font-weight: bold; }
.score-val { font-size: 28px; } .score-lvl { font-size: 12px; opacity: 0.8; }
.sc-a { border-color: #10b981; color: #10b981; } .sc-b { border-color: #3b82f6; color: #3b82f6; }
.score-badges { margin-top: 15px; }

/* 行情 */
.market-panel { height: 240px; }
.market-grid-top { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.m-item { background: #1e293b; padding: 8px; text-align: center; border-radius: 4px; }
.m-lbl { font-size: 12px; color: #64748b; } .m-v { font-size: 16px; font-weight: bold; }
.highlight { color: #facc15; } .danger { color: #f43f5e; } .up { color: #ef4444; } .down { color: #22c55e; }

/* AI */
.ai-panel { height: 240px; display: flex; flex-direction: column; }
.ai-box { background: #0f172a; flex: 1; padding: 10px; font-size: 13px; color: #cbd5e1; overflow-y: auto; border-left: 2px solid #8b5cf6; line-height: 1.5; }

/* 分隔符 */
.section-divider { border-left: 4px solid #38bdf8; padding-left: 10px; font-weight: bold; margin: 30px 0 15px; font-size: 16px; color: #e2e8f0; }

/* 核心财务 */
.core-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }
.c-card { padding: 10px; border-radius: 6px; text-align: center; }
.bg-blue { background: #1e3a8a; } .bg-green { background: #064e3b; } .bg-orange { background: #7c2d12; } .bg-purple { background: #581c87; } .bg-dark { background: #1e293b; }
.cv { font-size: 20px; font-weight: bold; } .cv.small { font-size: 16px; } .cl { font-size: 12px; opacity: 0.8; }

/* 迷你财务面板 */
.mini-panel { height: auto; } .p-head { color: #94a3b8; font-size: 14px; margin-bottom: 10px; display: flex; gap: 5px; }
.d-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.d-i { display: flex; flex-direction: column; background: #1e293b; padding: 5px; border-radius: 4px; }
.d-i span { font-size: 10px; color: #64748b; } .d-i b { font-size: 14px; } .d-i.danger b { color: #f43f5e; }

/* 物流色块 */
.m-box { padding: 15px; border-radius: 8px; text-align: center; }
.b-blue { background: linear-gradient(135deg, #2563eb, #1d4ed8); } .b-green { background: linear-gradient(135deg, #059669, #047857); }
.b-orange { background: linear-gradient(135deg, #d97706, #b45309); } .b-purple { background: linear-gradient(135deg, #7c3aed, #6d28d9); }
.mn { font-size: 28px; font-weight: bold; } .mt { font-size: 12px; opacity: 0.9; }

/* 风险与建议 */
.risk-card { background: #151e32; border-radius: 8px; border: 1px solid #2a3b55; height: 100%; overflow: hidden; }
.rc-head { padding: 10px; font-weight: bold; display: flex; align-items: center; gap: 5px; font-size: 14px; }
.warn-bg { background: #451a03; color: #fb923c; } .success-bg { background: #064e3b; color: #34d399; }
.rc-body { padding: 15px; } .risk-row, .sug-row { margin-bottom: 10px; font-size: 13px; color: #cbd5e1; display: flex; gap: 8px; align-items: flex-start;}

/* 底部黑条 */
.adv-panel { margin-top: 20px; display: flex; justify-content: space-around; text-align: center; height: auto; padding: 20px; }
.adv-i span { display: block; font-size: 12px; color: #64748b; margin-bottom: 5px; } .adv-i b { font-size: 18px; } .adv-i b.ok { color: #34d399; }

/* 页脚 */
.footer { margin-top: auto; padding: 40px 0 20px; background: #0f172a; border-top: 1px solid #1e293b; color: #94a3b8; font-size: 13px; }
.f-content { display: flex; justify-content: space-around; max-width: 1000px; margin: 0 auto 30px; }
.f-col h4 { color: #fff; margin-bottom: 15px; } .f-col a, .f-col span { display: block; margin-bottom: 8px; color: #64748b; cursor: pointer; display: flex; gap: 5px; align-items: center;}
.copyright { text-align: center; border-top: 1px solid #1e293b; padding-top: 20px; color: #475569; }
</style>