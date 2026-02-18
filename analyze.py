import os
import yfinance as yf
from ta.momentum import RSIIndicator
import requests
import json

# 从环境变量读取API密钥
API_KEY = os.environ.get("DASHSCOPE_API_KEY")

def get_stock_data(symbol):
    try:
        data = yf.download(symbol, period="1mo")
        if data.empty:
            return None, None
        price = data['Close'][-1]
        rsi = RSIIndicator(data['Close']).rsi()[-1]
        return round(price, 2), round(rsi, 2)
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None, None

def call_qwen(prompt):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-max",
        "input": {"messages": [{"role": "user", "content": prompt}]},
        "parameters": {"max_tokens": 200}
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result['output']['choices'][0]['message']['content']
    except Exception as e:
        return f"AI分析失败: {str(e)}"

def generate_report():
    stocks = ["AAPL", "TSLA", "NVDA", "600519.SS", "000858.SZ"]
    report = "# 📈 每日AI股票分析报告\n\n"
    report += "> 更新时间: $(date)\n\n"
    
    for symbol in stocks:
        price, rsi = get_stock_data(symbol)
        if price is None:
            analysis = "数据获取失败"
        else:
            prompt = f"""
你是一位专业股票分析师。请基于以下数据对{symbol}进行简明分析：
- 当前价格: ${price}
- RSI指标: {rsi}

要求：
1. 判断短期趋势（上涨/下跌/震荡）
2. 给出操作建议（买入/观望/卖出）
3. 用中文回答，不超过80字
"""
            analysis = call_qwen(prompt)
        
        report += f"## 📌 {symbol}\n"
        report += f"- 价格: ${price if price else 'N/A'}\n"
        report += f"- RSI: {rsi if rsi else 'N/A'}\n"
        report += f"- AI建议: {analysis}\n\n"
    
    # 保存为Markdown
    with open("report.md", "w") as f:
        f.write(report)

if __name__ == "__main__":
    generate_report()
