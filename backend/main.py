# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import math
import random
from spider import get_stock_base_info, get_real_quote, get_kline_data
from ai_service import get_risk_analysis

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class CompanyRequest(BaseModel):
    company_name: str


class DeterministicModel:
    def __init__(self, quote, volatility, trend):
        self.quote = quote
        self.mv = quote["total_mv"]
        self.pe = quote["pe_ratio"]
        self.price = quote["price"]
        self.volatility = volatility
        self.trend = trend
        self.mv_score = min(100, max(0, (math.log10(self.mv + 1) - 9) * 33))
        self.base_score = int(self.mv_score * 0.6 + 40 - self.volatility * 200)

    def generate_report(self):
        # 1. 格式化成交量 (核心修复)
        vol = self.quote["volume"]
        if vol > 1000000:
            vol_str = f"{vol / 1000000:.2f}M手"  # 百万手
        else:
            vol_str = f"{vol / 10000:.2f}万手"  # 万手

        # 2. 生成财务数据
        pb_ratio = round(self.pe / 15 * (1 + random.uniform(-0.2, 0.2)), 2)
        div_yield = round(max(0, (20 / self.pe) if self.pe > 0 else 0), 2)
        growth_factor = (self.pe / 20) if self.pe > 0 else 0.5
        rev_growth = round(8.0 * growth_factor + self.trend * 20, 2)

        # 3. 生成物流数据
        score = self.base_score
        stats = {
            "supplier_nodes": int(score * 0.5 + 10),
            "logistics_routes": int(score * 0.8 + 5),
            "warehouses": int(score * 0.2 + 2),
            "transport_efficiency": f"{min(99, int(score * 0.8 + 20))}%"
        }

        advanced = {
            "total_cost": f"${int(self.mv / 10000000 * 1.5):,}",
            "avg_delivery_time": f"{max(12, int(72 - score * 0.4))}h",
            "on_time_rate": f"{min(99.9, 85 + score * 0.15):.1f}%",
            "node_health": f"{min(100, int(score + 5))}%"
        }

        # 4. 风险与建议
        warnings = []
        if self.volatility > 0.03:
            warnings.append({"type": "high", "title": "供应商集中度过高", "desc": "Top5 占比 > 65%"})
        else:
            warnings.append({"type": "info", "title": "供应商结构健康", "desc": "Top5 占比 < 30%"})
        if self.trend < -0.05: warnings.append({"type": "medium", "title": "物流成本上升", "desc": "同比上升 12%"})
        warnings.append({"type": "info", "title": "地缘政治风险", "desc": "关注关税政策"})

        suggestions = [
            f"降低单一供应商占比至 {random.randint(30, 40)}% 以下",
            "优化路网，提升运输效率 15%",
            "建立实时预警机制",
            "提升库存周转率至 5次/年以上"
        ]

        return {
            "financial": {
                "core": {
                    "price": self.price, "mv": f"{self.mv / 100000000:.2f}亿", "pe": self.pe,
                    "revenue": f"{self.mv * 0.15 / 100000000:.2f}亿",
                    "volume": vol_str,  # 修复后的成交量
                    "high": round(self.price * 1.05, 2), "low": round(self.price * 0.95, 2)
                },
                "deep": {
                    "valuation": {"pb": pb_ratio, "ev": round(self.pe * 0.6, 2), "div": f"{div_yield}%", "pe": self.pe},
                    "growth": {"rev": f"{rev_growth}%", "profit": f"{round(rev_growth * 1.2, 2)}%",
                               "eps": f"{round(rev_growth * 0.9, 2)}%", "div": "5%"},
                    "health": {"cur": "1.05", "debt": "0.39", "int": "5.88"},
                    "risk": {"beta": "1.29", "vol": f"{self.volatility:.2%}", "sharpe": "1.48", "drawdown": "-21%"}
                }
            },
            "logistics": {
                "stats": stats, "advanced": advanced, "warnings": warnings, "suggestions": suggestions
            },
            "nodes": [
                {"name": f"节点-{i}", "status": "正常", "flow": random.randint(1000, 9000)} for i in range(5)
            ]
        }


@app.post("/assess")
async def assess_risk(request: CompanyRequest):
    base = get_stock_base_info(request.company_name)
    if not base: return {"status": "fail", "message": "未找到股票"}
    quote = get_real_quote(base["unified_code"])
    if not quote: return {"status": "fail", "message": "行情失败"}
    vol, trend = get_kline_data(base["unified_code"])

    model = DeterministicModel(quote, vol, trend)
    data = model.generate_report()

    # AI 分析
    ai_text = get_risk_analysis(base["name"], {"mv": quote["total_mv"]}, {"score": model.base_score, "level": "AAA",
                                                                          "market_data": {"volatility": vol,
                                                                                          "trend": trend},
                                                                          "stats": data["logistics"]["stats"]})

    return {
        "status": "success",
        "base": {"name": quote["name"], "code": base["code"], "score": model.base_score, "level": "AAA"},
        "stock": {"price": quote["price"], "pe": quote["pe_ratio"], "vol": f"{vol:.2%}", "trend": f"{trend:.2%}"},
        "data": data,
        "ai_analysis": ai_text
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)