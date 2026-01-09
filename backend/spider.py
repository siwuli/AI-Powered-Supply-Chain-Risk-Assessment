# backend/spider.py
import requests
import re
import pandas as pd
import akshare as ak  # 保留用于获取K线
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://eastmoney.com/"
}


def get_stock_base_info(keyword):
    """
    【核心升级】支持 沪/深/港/美 全球搜索
    返回: name, code, secid (东方财富核心ID)
    """
    url = "https://searchapi.eastmoney.com/api/suggest/get"
    params = {
        "input": keyword,
        "type": "14",
        "token": "D43BF722C8E33BDC906FB84D85E326E8"
    }
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=5)
        data = res.json()
        if "QuotationCodeTable" in data and data["QuotationCodeTable"]["Data"]:
            # 取第一个匹配度最高的结果（不再过滤A股）
            item = data["QuotationCodeTable"]["Data"][0]

            code = item["Code"]
            name = item["Name"]
            mkt = item["MarketType"]
            quote_id = item["QuoteID"]  # 这是一个很关键的字段

            # 构造 SecID (这是获取实时行情的钥匙)
            # 逻辑：东方财富内部 1=沪, 0=深, 116=港, 105=美
            # 直接使用 Search 接口返回的 QuoteID 其实最稳，或者根据 MarketType 拼装

            # 简单映射逻辑：
            # A股: MarketType 1->1.xxx, 2->0.xxx
            # 港股: MarketType 5->116.xxx
            # 美股: MarketType 10->105.xxx

            # 为了数据绝对准确，我们尝试直接返回 code 和 mkt，由下一步处理
            return {
                "name": name,
                "code": code,
                "mkt": mkt,
                "unified_code": quote_id if quote_id != "0" else f"{mkt}.{code}"  # 容错
            }

    except Exception as e:
        print(f"[Error] 搜索失败: {e}")
    return None


def get_real_quote(secid):
    """
    【数据清洗】获取绝对真实的：股价、市值、市盈率、换手率
    接口：push2.eastmoney.com snapshot
    """
    # 这个接口是东方财富网页版通用的，数据极其精准
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    # secid 修正：
    # 搜索返回的 QuoteID 有时带市场有时候不带。
    # 港股腾讯通常是 116.00700

    params = {
        "secid": secid,
        "fltt": "2",
        "invt": "2",
        "fields": "f43,f57,f58,f169,f170,f46,f44,f45,f116,f60"
        # f43: 最新价, f57: 代码, f58: 名称, f116: 总市值(绝对值), f169: 市值变动, f170: 追涨
        # f116 是总市值， f162 是市盈率(动)
    }
    # 补充更多字段：f116=总市值, f162=PE(动), f167=市净率, f168=换手率
    params["fields"] += ",f116,f162,f167,f168"

    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=5)
        data = res.json()
        if data and "data" in data and data["data"]:
            d = data["data"]

            # 数据清洗：将 - 转化为 0
            def clean_num(val):
                return 0 if val == "-" else val

            return {
                "price": float(clean_num(d.get("f43", 0))),
                "total_mv": float(clean_num(d.get("f116", 0))),  # 真实总市值
                "pe_ratio": float(clean_num(d.get("f162", 0))),  # 真实市盈率
                "turnover": float(clean_num(d.get("f168", 0))),  # 真实换手率
                "code": d.get("f57"),
                "name": d.get("f58")
            }
    except Exception as e:
        print(f"[Error] 行情获取失败: {e}")

    return None


def get_kline_data(secid):
    """
    获取K线计算波动率 (AkShare 对港股支持较弱，改用 API 直接计算)
    """
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f51",
        "klt": "101",  # 日K
        "fqt": "1",  # 前复权
        "end": "20500101",
        "lmt": "90"  # 最近90天
    }
    try:
        res = requests.get(url, params=params, headers=HEADERS)
        data = res.json()
        if data["data"] and data["data"]["klines"]:
            klines = data["data"]["klines"]
            # 解析收盘价 (f53)
            closes = [float(x.split(",")[2]) for x in klines]

            # 纯数学计算，绝对准确
            import numpy as np
            closes_np = np.array(closes)
            volatility = np.std(closes_np) / np.mean(closes_np)
            trend = (closes_np[-1] - closes_np[0]) / closes_np[0]

            return volatility, trend
    except:
        pass
    return 0.02, 0.0  # 默认值


if __name__ == "__main__":
    # 单元测试：必须能通过 腾讯(港股) 和 比亚迪(A股)
    print("Testing Tencent (HK)...")
    base = get_stock_base_info("腾讯控股")
    print(base)
    if base:
        quote = get_real_quote(base["unified_code"])
        print(quote)  # 这里必须显示几万亿的市值

    print("\nTesting BYD (A)...")
    base = get_stock_base_info("比亚迪")
    if base:
        quote = get_real_quote(base["unified_code"])
        print(quote)