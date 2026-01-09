🛡️ AI + 供应链金融大数据风控评分卡 (AI-Powered Supply Chain Risk Assessment System)
"虚实结合"的下一代风控系统：基于实时金融数据（实）驱动供应链运营推演（虚），结合大模型生成专业信贷评估报告。

📖 1. 项目背景与简介 (Introduction)
在传统的供应链金融风控中，核心企业与上下游中小企业的信用评估往往存在数据获取难、维度单一、时效性差的问题。

本项目构建了一个端到端的智能风控平台，通过以下三步解决上述痛点：

实时抓取：对接东方财富/AkShare 接口，获取上市企业实时的股价、市值、PE、波动率等核心金融指标。

确定性建模：独创 DeterministicModel 映射算法，基于企业的资金体量与市场情绪，科学推算其供应链的节点规模、物流效率、库存周转率。

AI 深度决策：集成 DeepSeek V3 大语言模型，模拟首席风控官（CRO）的思维，输出包含风险归因、授信建议的深度研报。

🏗️ 2. 系统架构 (System Architecture)
系统采用 前后端分离 (B/S) 架构，数据流向如下：

代码段

graph LR
    User[用户输入企业名] --> Frontend[Vue3 前端可视化]
    Frontend -- HTTP Request --> Backend[FastAPI 后端服务]
    Backend -- 爬虫 --> External[东方财富/AkShare API]
    External -- 实时行情 --> Backend
    Backend -- 算法推演 --> Logic[确定性映射模型]
    Backend -- Prompt --> AI[DeepSeek V3 LLM]
    AI -- 风控研报 --> Backend
    Backend -- JSON Response --> Frontend
    Frontend -- 渲染 --> Charts[ECharts 雷达图/柱状图]
🛠️ 3. 技术栈详解 (Tech Stack)
🔙 后端 (Backend)
Core Framework: FastAPI (异步高性能，自动生成 API 文档)

Data Spider: AkShare, Requests (处理反爬与数据清洗)

Data Analysis: Pandas, NumPy (计算波动率、夏普比率、最大回撤)

AI Integration: OpenAI SDK (复用接口协议对接 DeepSeek)

Model Logic: 自研确定性映射算法 (Deterministic Mapping Algorithm)

🔜 前端 (Frontend)
Framework: Vue 3 (Composition API) + Vite (极速构建)

UI Library: Element Plus (暗黑科技风定制)

Visualization: ECharts 5.0 (雷达图、动态渐变柱状图)

Network: Axios (拦截器封装)

Animation: Animate.css (平滑入场动画)

📂 4. 目录结构说明 (Directory Structure)
Plaintext

Supply_Chain_Risk_System/
│
├── run.bat                 # 【核心】全自动一键启动脚本 (环境检测+依赖安装+服务启动)
├── README.md               # 项目核心文档
│
├── backend/                # --- 后端服务层 ---
│   ├── main.py             # 程序入口：定义 API 路由、整合数据、返回结果
│   ├── spider.py           # 爬虫模块：负责清洗 F10 资料、K线数据、实时盘口
│   ├── ai_service.py       # AI 模块：封装 Prompt 提示词工程，对接 DeepSeek
│   ├── config.py           # 配置模块：存放 DEEPSEEK_API_KEY 等敏感配置
│   └── requirements.txt    # 依赖清单：后端所需的 Python 库列表
│
└── frontend/               # --- 前端视图层 ---
    ├── index.html          # 网页入口
    ├── vite.config.js      # Vite 配置 (代理设置、路径别名)
    ├── package.json        # 项目描述文件 (定义 npm 脚本和依赖)
    └── src/
        ├── main.js         # Vue 全局入口
        └── App.vue         # 【核心】主界面组件 (包含所有 UI 逻辑、图表渲染、交互代码)
⚡ 5. 快速启动指南 (Quick Start)
我们为 Windows 用户提供了零门槛一键启动方案。

✅ 环境准备 (Prerequisites)
请确保您的电脑已安装：

Python 3.8+ (请勾选 "Add Python to PATH")

Node.js 16.0+ (LTS 版本即可)

🚀 启动步骤
下载并解压项目文件夹。

进入根目录，找到 run.bat 文件。

直接双击运行。

脚本运行流程：

自动检测 Python 和 Node.js 环境。

后端：自动创建虚拟环境 (venv) -> 自动配置清华镜像源 -> 安装 requirements.txt。

前端：自动识别 node_modules -> 缺失则自动执行 npm install 下载依赖 (含 Vite)。

自动打开两个黑色命令行窗口（分别运行后端和前端）。

自动唤起浏览器访问 http://localhost:5173。

📊 6. 核心功能模块 (Core Modules)
A. 实时金融看板 (Real-time Financials)
数据源：直接接入二级市场实时交易数据。

展示指标：

核心：股价、市值、PE-TTM、成交量。

深度：EV/EBITDA、股息率、流动比率、利息覆盖倍数。

风险：90日波动率 (Volatility)、Beta 系数、最大回撤。

B. 供应链运营推演 (Operations Simulation)
基于 backend/main.py 中的数学模型：

节点规模：基于 log(市值) 映射全球供应商与仓储中心数量。

物流效率：基于 股价趋势 与 波动率 动态调整运输准时率。

成本分析：模拟计算全球各区域（华东/华南/海外）的流量吞吐与运营成本。

C. 可视化图表 (Data Visualization)
供应链韧性雷达 (Radar Chart)：多维度评估企业的“供应稳定性、物流可靠性、仓储效率”。

流量成本分析 (Bar/Line Chart)：双轴图表，直观展示各物流节点的业务量与成本消耗对比。

D. AI 智能研报 (AI Analysis)
DeepSeek V3 模型根据结构化数据生成：

综合评分：AAA/AA/A/B 分级。

风险预警：识别“供应商集中度过高”、“物流成本激增”等隐患。

改进建议：给出数字化转型、库存优化等具体落地策略。

❓ 7. 常见问题排查 (Troubleshooting)
Q1: 双击脚本后闪退，什么都没看到？

原因：通常是 Windows 记事本保存的编码问题。

解决：确保 run.bat 是 ANSI 编码，或者使用我们提供的纯英文版脚本。建议右键脚本 -> 编辑 -> 另存为 -> 编码选择 ANSI。

Q2: 提示 'pip' 不是内部或外部命令？

原因：安装 Python 时未勾选 "Add to PATH"。

解决：我们的新版脚本已通过 python -m pip 绕过此问题。只要 python 命令能用，脚本就能跑。

Q3: 提示 'vite' 不是内部或外部命令？

原因：前端依赖 node_modules 缺失或安装不完整。

解决：删除 frontend/node_modules 文件夹，重新运行 run.bat，脚本会自动重新下载 Vite。

Q4: 网页显示“连接服务器失败”？

原因：后端黑色窗口被关闭，或者报错停止了。

解决：请检查后端窗口的报错信息。常见原因是 API Key 额度耗尽，或网络无法连接东方财富接口。

📜 8. 版权与声明 (License & Disclaimer)
Copyright: © 2026 智链风控 (AI Supply Chain Risk).

Data Source: 本项目行情数据源自公开网络接口，仅用于科研教学演示，不构成任何投资建议。

License: MIT License. 允许自由复制、修改和分发，但请保留原作者版权声明。
