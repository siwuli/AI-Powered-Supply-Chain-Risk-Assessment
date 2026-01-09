# 供应链风控评估器（Supply Chain Risk Evaluator）



## 一、项目总体说明



本项目是一个 **“基于真实上市公司数据 + 模拟供应链因子 + 大模型分析”** 的综合风险评估系统。



系统目标：



* 输入一个公司名称（上市公司）

* 自动获取 **股票基础信息、行情、波动率、趋势**

* 构造一组 **可解释的供应链风险模拟指标**

* 计算 **量化风险评分（Risk Score）**

* 调用 **DeepSeek 大模型**，生成一份“像咨询报告一样”的风险分析文本



整体采用 **前后端分离架构**：



```text

前端（Vite + 原生 JS）  -->  FastAPI 后端  -->  数据爬虫 / AI 服务

```



---



## 二、项目目录结构（精确到文件）



```text

供应链风控评估器/

│

├── backend/                     # 后端核心

│   ├── main.py                  # FastAPI 主入口（接口 + 风控逻辑）

│   ├── spider.py                # 股票数据爬虫（东方财富 / AkShare）

│   ├── ai\_service.py            # DeepSeek 大模型分析服务

│   ├── config.py                # API Key / Base URL 配置

│   ├── requirements.txt         # Python 依赖

│   └── venv/                    # 本地虚拟环境（可删除）

│

├── frontend/                    # 前端界面

│   ├── index.html               # 页面结构

│   ├── src/

│   │   ├── main.js              # 前端核心逻辑（请求后端 + 渲染结果）

│   │   └── style.css            # 页面样式

│   ├── package.json

│   └── vite.config.js

│

└── README.md

```



---



## 三、系统工作流程（从输入到结果）



```text

用户输入公司名

&nbsp;  ↓

前端 POST /analyze

&nbsp;  ↓

后端解析公司 → 股票代码

&nbsp;  ↓

获取实时股价 / PE / 波动率 / 趋势

&nbsp;  ↓

构造模拟供应链数据（物流 / 供应商 / 库存）

&nbsp;  ↓

计算综合风险分数

&nbsp;  ↓

调用 DeepSeek 生成风险分析报告

&nbsp;  ↓

返回 JSON → 前端渲染

```



---



## 四、后端详解（FastAPI）



### 4.1 main.py —— 系统核心



#### （1）应用初始化



```python

app = FastAPI()

app.add\_middleware(

&nbsp;   CORSMiddleware,

&nbsp;   allow\_origins=\["*"],

&nbsp;   allow\_methods=\["*"],

&nbsp;   allow\_headers=\["*"],

)

```



作用：



* 创建 API 服务

* 允许前端跨域访问



---



#### （2）请求数据结构定义



```python

class CompanyRequest(BaseModel):

&nbsp;   company\_name: str

```



前端只需要传：



```json

{

&nbsp; "company\_name": "贵州茅台"

}

```



---



#### （3）核心接口 `/analyze`



```python

@app.post("/analyze")

def analyze\_company(req: CompanyRequest):

```



该接口内部逻辑可以拆解为 **5 个阶段**。



---



### 4.2 股票数据获取（spider.py）



#### （1）搜索股票代码



```python

def get\_stock\_base\_info(keyword):

&nbsp;   url = "https://searchapi.eastmoney.com/api/suggest/get"

```



作用：



* 将「公司名称」 → 「股票代码 + 市场」



返回示例：



```python

{

&nbsp; "code": "600519",

&nbsp; "name": "贵州茅台",

&nbsp; "market": "SH"

}

```



---



#### （2）实时行情数据



```python

def get\_real\_quote(code, market):

```



返回内容包括：



* 当前价格 price

* 市盈率 pe\_ratio

* 公司名称 name



---



#### （3）K 线风险指标



```python

std = np.std(prices) / np.mean(prices)

trend = (prices\[-1] - prices\[0]) / prices\[0]

```



含义：



* **波动率**：价格不稳定程度（风险）

* **趋势**：上涨 or 下跌



---



### 4.3 供应链风险模拟（核心思想）



> ⚠️ 本项目不是直接爬供应链，而是**构造可解释的仿真模型**



```python

logistics\_delay = random.uniform(0.05, 0.25)

supplier\_risk = random.uniform(0.1, 0.4)

inventory\_pressure = random.uniform(0.1, 0.5)

```



每个指标都有现实意义：



* 物流延迟率

* 供应商集中度风险

* 库存积压压力



---



### 4.4 综合风险评分模型



```python

score = (

&nbsp;   0.3 * stock\_risk +

&nbsp;   0.4 * supply\_chain\_risk +

&nbsp;   0.3 * financial\_stability

)

```



评分区间：



* 0 ~ 100

* 分数越低，风险越高



---



## 五、AI 风险分析模块（ai\_service.py）



### 5.1 DeepSeek 客户端初始化



```python

client = OpenAI(

&nbsp;   api\_key=DEEPSEEK\_API\_KEY,

&nbsp;   base\_url=DEEPSEEK\_BASE\_URL

)

```



---



### 5.2 Prompt 构造逻辑



```python

system\_prompt = "你是一名专业的供应链与金融风险分析顾问"

```



```python

user\_content = f"""

公司：{company\_name}

行业：{industry}

综合风险评分：{score}

物流风险：{logistics}

供应商风险：{supplier}

库存风险：{inventory}

"""

```



特点：



* 明确角色

* 明确数据来源

* 防止胡编乱造



---



### 5.3 AI 输出示例



* 风险总体判断

* 主要风险来源

* 改进建议

* 短期 / 中长期展望



---



## 六、前端结构说明



### 6.1 index.html



* 输入框（公司名）

* 分析按钮

* 结果展示区域



---



### 6.2 main.js 核心逻辑



```js

fetch("http://127.0.0.1:8080/analyze", {

&nbsp; method: "POST",

&nbsp; headers: { "Content-Type": "application/json" },

&nbsp; body: JSON.stringify({ company\_name })

})

```



接收后端 JSON 后：



* 渲染评分

* 渲染指标

* 渲染 AI 文本报告



---



## 七、如何运行项目



### 后端



```bash

cd backend

pip install -r requirements.txt

python main.py

```



### 前端



```bash

cd frontend

npm install

npm run dev

```



---



## 八、项目设计亮点



1\. **真实金融数据 + AI 解释**

2\. 供应链风险可量化、可扩展

3\. 架构清晰，适合课程设计 / 毕设 / 展示项目

4\. AI 不“拍脑袋”，而是基于结构化数据生成结论



---



## 九、可扩展方向



* 接入真实企业供应链数据

* 多模型对比（DeepSeek / GPT）

* 风险历史趋势图

* 企业对比分析

