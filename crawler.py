import requests
from bs4 import BeautifulSoup
import json
import os
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    filename='crawler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_aluminum_price():
    """爬取上海有色网电解铝价格"""
    url = "https://www.ccmn.cn/priceinfo/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.ccmn.cn/"
    }
    
    try:
        # 发送请求并解析页面
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 定位电解铝价格 - 根据实际页面结构调整
        price_box = soup.select_one('.single-metal .price-value')
        if price_box:
            price = price_box.text.strip().replace(',', '')
            price_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 返回结构化的价格数据
            return {
                "price": price,
                "currency": "CNY",
                "unit": "元/吨",
                "lastUpdated": price_date,
                "source": "长江有色网"
            }
        else:
            logging.warning("未找到价格元素，页面结构可能已变化")
            return None
            
    except Exception as e:
        logging.error(f"爬取失败: {str(e)}")
        return None

def update_data_file():
    """更新数据文件"""
    data = fetch_aluminum_price()
    if data:
        try:
            # 写入JSON文件
            with open('price-data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"数据更新成功: {data['price']}")
            return True
        except Exception as e:
            logging.error(f"文件写入失败: {str(e)}")
    
    return False

def main():
    """主函数：定时执行任务"""
    while True:
        current_hour = datetime.now().hour
        if current_hour == 10:  # 每天10点执行
            if update_data_file():
                print("价格数据更新完成!")
            else:
                print("数据更新失败，请查看日志")
        
        # 等待1小时再检查
        time.sleep(3600)

if __name__ == "__main__":
    main()
