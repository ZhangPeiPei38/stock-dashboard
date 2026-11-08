import requests
import json
import datetime
import os

# 配置区 - 后续替换成你的股票代码
STOCKS = [
    {"code": "sh600519", "name": "贵州茅台"},
    {"code": "sz000001", "name": "平安银行"}
]
INDEXES = [
    {"code": "sh000001", "name": "上证指数"},
    {"code": "sz399001", "name": "深证成指"}
]
DATA_LEN = 60  # 保留60天历史数据

def is_trade_day():
    """判断是否为交易日（简易判断：排除周末，节假日可后续补充）"""
    today = datetime.date.today()
    return today.weekday() < 5

def get_kline(code):
    """获取单只股票/指数的日线数据"""
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
    params = {
        "symbol": code,
        "scale": 240,
        "ma": "no",
        "datalen": DATA_LEN
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = json.loads(res.text)
        # 计算涨跌额和涨跌幅
        for i in range(len(data)):
            if i == 0:
                pre_close = float(data[i]['open'])
            else:
                pre_close = float(data[i-1]['close'])
            close = float(data[i]['close'])
            change = round(close - pre_close, 2)
            change_pct = round((change / pre_close) * 100, 2)
            data[i]['change'] = change
            data[i]['change_pct'] = change_pct
        return data
    except Exception as e:
        print(f"获取 {code} 数据失败: {e}")
        return []

def main():
    if not is_trade_day():
        print("非交易日，跳过采集")
        return
    
    result = {
        "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "indexes": [],
        "stocks": []
    }

    # 采集大盘指数
    for idx in INDEXES:
        kline = get_kline(idx['code'])
        if kline:
            latest = kline[-1]
            result['indexes'].append({
                "code": idx['code'],
                "name": idx['name'],
                "price": float(latest['close']),
                "change": latest['change'],
                "change_pct": latest['change_pct'],
                "kline": kline
            })

    # 采集个股
    for stock in STOCKS:
        kline = get_kline(stock['code'])
        if kline:
            result['stocks'].append({
                "code": stock['code'],
                "name": stock['name'],
                "kline": kline
            })

    # 保存数据
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("数据采集完成，已保存到 data.json")

if __name__ == "__main__":
    main()
