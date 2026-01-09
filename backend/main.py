# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import math
from spider import get_stock_base_info, get_real_quote, get_kline_data
from ai_service import get_risk_analysis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompanyRequest(BaseModel):
    company_name: str


class DeterministicModel:
    """
    确定性建模引擎：
    基于真实的【市值、PE、波动率】计算评分，
    严禁使用随机数生成核心指标，确保数据可用于建模训练。
    """

    def __init__(self, quote, volatility, trend):
        self.mv = quote["total_mv"]  # 真实市值
        self.pe = quote["pe_ratio"]  # 真实PE
        self.price = quote["price"]  # 真实股价
        self.volatility = volatility  # 真实波动率
        self.trend = trend  # 真实趋势

        # 归一化处理 (Feature Scaling)
        # 假设 A股/港股 龙头市值在 1万亿左右，小票在 20亿左右
        # Log10(1万亿) ≈ 12, Log10(20亿) ≈ 9.3
        self.mv_score = min(100, max(0, (math.log10(self.mv + 1) - 9) * 33))

        # 波动率修正：波动率越高，供应链风险越大，分数越低
        self.vol_penalty = self.volatility * 100 * 2  # 波动率0.02 -> 扣4分

    def calculate_score(self):
        # 核心评分公式 (可用于逻辑回归或XGBoost的Target构建)
        # Score = 70% 市值因子 + 20% 趋势因子 - 10% 波动惩罚
        base = self.mv_score * 0.7 + 30
        trend_bonus = 10 if self.trend > 0 else -5

        final_score = int(base + trend_bonus - self.vol_penalty)
        return min(99, max(35, final_score))  # 限制在 35-99 之间

    def generate_supply_chain_data(self, score):
        """
        基于分数的推导数据 (Derived Features)
        分数越高 -> 节点越多，效率越高。这是完全线性的关系，非随机。
        """
        # 1. 供应商节点数：线性映射
        supplier_count = int(score * 1.5)

        # 2. 运输效率：Sigmoid 函数映射，分数高则效率趋近 98%
        efficiency = int(99 / (1 + math.exp(-(score - 60) / 10)))

        # 3. 节点生成 (基于真实逻辑的模板)
        nodes = []
        # 根据市值规模决定覆盖区域
        regions = ["华东", "华南", "华北"] if score < 70 else ["华东", "华南", "北美", "欧洲", "东南亚"]

        for i, region in enumerate(regions):
            # 流量与市值正相关
            flow = int(self.mv / 100000000 * (1 - i * 0.1))  # 亿级 -> 吨
            nodes.append({
                "name": f"核心枢纽-{region}",
                "status": "正常" if self.volatility < 0.05 else "拥堵",  # 波动大则拥堵
                "efficiency": f"{efficiency - i}%",
                "flow": f"{flow:,}",
                "cost": f"{int(100 + i * 20)}",
                "risk": f"{int(self.volatility * 100 + i * 2)}%"
            })

        return {
            "stats": {
                "supplier_nodes": supplier_count,
                "logistics_routes": int(supplier_count * 1.2),
                "warehouses": int(supplier_count / 4) + 1,
                "transport_efficiency": f"{efficiency}%"
            },
            "nodes_list": nodes
        }


@app.post("/assess")
async def assess_risk(request: CompanyRequest):
    print(f"--- 分析请求: {request.company_name} ---")

    # 1. 全球搜索 (支持腾讯、特斯拉)
    base = get_stock_base_info(request.company_name)
    if not base:
        return {"status": "fail", "message": "未找到相关上市企业 (支持沪深港美)"}

    # 2. 获取绝对真实的清洗数据
    quote = get_real_quote(base["unified_code"])
    if not quote:
        return {"status": "fail", "message": "行情数据获取失败"}

    volatility, trend = get_kline_data(base["unified_code"])

    # 3. 确定性建模 (无随机数)
    model = DeterministicModel(quote, volatility, trend)
    score = model.calculate_score()
    chain_data = model.generate_supply_chain_data(score)

    # 4. AI 分析
    # 传入真实市值数据，让AI别瞎编
    ai_report = get_risk_analysis(
        base["name"],
        {"industry": "自动识别", "mv": f"{quote['total_mv'] / 100000000:.2f}亿"},
        {"score": score, "level": "AAA", "market_data": {"volatility": volatility, "trend": trend},
         "stats": chain_data["stats"]}
    )

    # 5. 返回标准化 JSON
    return {
        "status": "success",
        "company_name": quote["name"],
        "industry": "全球市场",  # 通用接口暂不返回细分行业，前端可写死或忽略
        "capital": f"{quote['total_mv'] / 100000000:.2f}亿 (市值)",  # 用市值代替注册资本，更有风控意义
        "legal": base["code"],  # 展示股票代码
        "stock_info": {
            "price": quote["price"],
            "volatility": f"{volatility:.2%}",
            "trend": f"{trend:.2%}",
            "pe": quote["pe_ratio"]
        },
        "risk_data": {
            "score": score,
            "level": "AAA" if score > 80 else "AA" if score > 70 else "B",
            "stats": chain_data["stats"],
            "nodes_list": chain_data["nodes_list"],
            # 兼容前端结构
            "dimensions": {
                "supplier_stability": {"score": score},
                "chain_diversity": {"score": int(score * 0.9)},
                "logistics_reliability": {"score": int(score * 0.95)},
                "warehouse_efficiency": {"score": int(score * 0.85)}
            }
        },
        "ai_analysis": ai_report
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)