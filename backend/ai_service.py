# backend/ai_service.py
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# 初始化客户端
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def get_risk_analysis(company_name, profile, sim_result):
    """
    让 DeepSeek 根据【真实身份】+【股市因子】+【模拟供应链数据】生成报告
    """

    # 1. 提取关键指标，构建上下文
    industry = profile.get("industry", "未知行业")
    score = sim_result["score"]
    level = sim_result["level"]
    volatility = sim_result["market_data"]["volatility"]  # 真实波动率
    trend = sim_result["market_data"]["trend"]  # 真实趋势

    # 2. 构建超级提示词 (System Prompt)
    system_prompt = """
    你是一位拥有20年经验的供应链金融风控专家。请基于提供的企业数据，撰写一份《供应链信用风险评估报告》。

    要求：
    1. 风格专业、犀利、客观，类似投行研报。
    2. 必须结合“股市行情”与“供应链韧性”进行关联分析（例如：股价波动大导致供应链成本不可控）。
    3. 分三段输出：【总体评价】、【风险归因】、【授信建议】。
    4. 字数控制在 300 字以内，不要废话。
    """

    user_content = f"""
    分析对象：{company_name}
    所属行业：{industry}

    【量化评估数据】
    - 供应链综合评分：{score}分 (等级：{level})
    - 市场波动率：{volatility} (反映外部风险)
    - 股价趋势：{trend} (反映经营预期)
    - 核心供应商节点数：{sim_result['stats']['supplier_nodes']} 个
    - 物流运输效率：{sim_result['stats']['transport_efficiency']}

    请分析该企业在当前的股市波动下，其供应链是否存在中断风险？
    """

    try:
        print(f"   [AI] 正在调用 DeepSeek 分析 {company_name} ...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            stream=False,
            temperature=0.4  # 稍微严谨一点
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"   [Error] AI分析服务异常: {e}")
        return "AI 服务暂时不可用，请检查网络或 API Key。"