import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

def fetch_aluminum_price():
    url = "https://www.ccmn.cn/priceinfo/al"  # 长江有色网铝价格页面
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.ccmn.cn/"
    }
    
    try:
        # 发送请求并解析页面
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查HTTP状态码
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # 定位电解铝价格（示例选择器，需根据实际页面调整）
        price_element = soup.select_one("div.price-data:contains('A00铝') + span.price-value")
        if price_element:
            price = price_element.text.strip()  # 提取价格文本
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存到CSV文件
            with open('aluminum_prices.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, price])
            print(f"[{timestamp}] 成功爬取电解铝价格：{price}元/吨")
        else:
            print("未找到价格元素，请检查页面结构或选择器！")
    
    except Exception as e:
        print(f"爬取失败：{str(e)}")

# 配置定时任务（每天10点执行）
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_aluminum_price, 'cron', hour=10, minute=0)  # 每天10:00执行
    print("爬虫定时任务已启动，等待每天10点执行...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("任务已终止")
