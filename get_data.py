import requests
import json
import datetime
import os

# 配置区 - 自选股列表（55只）
STOCKS = [
    {"code": "sh600722", "name": "金牛化工"},
    {"code": "sh600378", "name": "昊华科技"},
    {"code": "sh600096", "name": "云天化"},
    {"code": "sh600343", "name": "航天动力"},
    {"code": "sh600900", "name": "长江电力"},
    {"code": "sh601330", "name": "绿色动力"},
    {"code": "sz002428", "name": "云南锗业"},
    {"code": "sh688160", "name": "步科股份"},
    {"code": "sh688392", "name": "骄成超声"},
    {"code": "sh600348", "name": "华阳股份"},
    {"code": "sz002348", "name": "高乐股份"},
    {"code": "sh600105", "name": "永鼎股份"},
    {"code": "sh603259", "name": "药明康德"},
    {"code": "sh605123", "name": "派克新材"},
    {"code": "sz001337", "name": "四川黄金"},
    {"code": "sz002142", "name": "宁波银行"},
    {"code": "sz002979", "name": "雷赛智能"},
    {"code": "sh603906", "name": "龙蟠科技"},
    {"code": "sh601838", "name": "成都银行"},
    {"code": "sz002938", "name": "鹏鼎控股"},
    {"code": "sz002980", "name": "华盛昌"},
    {"code": "sz002916", "name": "深南电路"},
    {"code": "sh603773", "name": "沃格光电"},
    {"code": "sh603618", "name": "杭电股份"},
    {"code": "sz000938", "name": "紫光股份"},
    {"code": "sz002430", "name": "杭氧股份"},
    {"code": "sz002463", "name": "沪电股份"},
    {"code": "sz002008", "name": "大族激光"},
    {"code": "sh600176", "name": "中国巨石"},
    {"code": "sh600703", "name": "三安光电"},
    {"code": "sz002384", "name": "东山精密"},
    {"code": "sh600498", "name": "烽火通信"},
    {"code": "sh600487", "name": "亨通光电"},
    {"code": "sz000547", "name": "航天发展"},
    {"code": "sz002371", "name": "北方华创"},
    {"code": "sz002792", "name": "通宇通讯"},
    {"code": "sz002413", "name": "雷科防务"},
    {"code": "sz002049", "name": "紫光国微"},
    {"code": "sz000988", "name": "华工科技"},
    {"code": "sh600276", "name": "恒瑞医药"},
    {"code": "sh605099", "name": "共创草坪"},
    {"code": "sh601899", "name": "紫金矿业"},
    {"code": "sz000831", "name": "中国稀土"},
    {"code": "sh603459", "name": "红板科技"},
    {"code": "sh601138", "name": "工业富联"},
    {"code": "sh601857", "name": "中国石油"},
    {"code": "sh601869", "name": "长飞光纤"},
    {"code": "sh600938", "name": "中国海油"},
    {"code": "sh600584", "name": "长电科技"},
    {"code": "sh600118", "name": "中国卫星"},
    {"code": "sh600406", "name": "国电南瑞"},
    {"code": "sh600268", "name": "国电南自"},
    {"code": "sh600879", "name": "航天电子"},
    {"code": "sz002738", "name": "中矿资源"},
    {"code": "sh600362", "name": "江西铜业"},
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
