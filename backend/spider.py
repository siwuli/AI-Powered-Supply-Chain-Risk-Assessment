# backend/spider.py
import requests
import re
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://eastmoney.com/"
}


def get_stock_base_info(keyword):
    """搜索股票代码 (支持全市场)"""
    url = "https://searchapi.eastmoney.com/api/suggest/get"
    params = {
        "input": keyword, "type": "14", "token": "D43BF722C8E33BDC906FB84D85E326E8"
    }
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=5)
        data = res.json()
        if "QuotationCodeTable" in data and data["QuotationCodeTable"]["Data"]:
            item = data["QuotationCodeTable"]["Data"][0]
            return {
                "name": item["Name"],
                "code": item["Code"],
                "unified_code": item["QuoteID"] if item["QuoteID"] != "0" else f"{item['MarketType']}.{item['Code']}"
            }
    except Exception as e:
        print(f"[Error] 搜索失败: {e}")
    return None


def get_real_quote(secid):
    """
    获取实时行情
    修正：增加 f47 (成交量-手), f48 (成交额)
    """
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": secid,
        "fltt": "2", "invt": "2",
        # f43:价, f116:市值, f162:PE, f167:PB, f47:成交量, f48:成交额, f168:换手率
        "fields": "f43,f57,f58,f116,f162,f167,f47,f48,f168"
    }
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=5)
        data = res.json()
        if data and "data" in data and data["data"]:
            d = data["data"]

            def clean(v): return 0 if v == "-" else float(v)

            return {
                "code": d.get("f57"),
                "name": d.get("f58"),
                "price": clean(d.get("f43")),
                "total_mv": clean(d.get("f116")),
                "pe_ratio": clean(d.get("f162")),
                "volume": clean(d.get("f47")),  # 成交量 (单位：手)
                "amount": clean(d.get("f48")),  # 成交额
                "turnover_rate": clean(d.get("f168"))  # 换手率
            }
    except Exception as e:
        print(f"[Error] 行情获取失败: {e}")
    return None


def get_kline_data(secid):
    """获取K线计算波动率"""
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid, "fields1": "f1", "fields2": "f53", "klt": "101", "fqt": "1", "end": "20500101", "lmt": "90"
    }
    try:
        res = requests.get(url, params=params, headers=HEADERS)
        data = res.json()
        if data["data"] and data["data"]["klines"]:
            closes = [float(x.split(",")[0]) for x in data["data"]["klines"]]
            import numpy as np
            arr = np.array(closes)
            return np.std(arr) / np.mean(arr), (arr[-1] - arr[0]) / arr[0]
    except:
        pass
    return 0.02, 0.0