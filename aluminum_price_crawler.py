import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

def crawl_aluminum_price():
    url = "https://www.ccmn.cn/priceinfo/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    try:
        # 1. 发送请求并验证响应
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # 自动处理非200状态码
        response.encoding = 'utf-8'
        
        # 2. 解析关键数据
        soup = BeautifulSoup(response.text, 'lxml')
        price_table = soup.select_one("table.table-data")  # 根据实际页面结构调整选择器
        
        if not price_table:
            raise ValueError("未找到价格表格，请检查页面结构变更")
        
        # 3. 定位铝价数据行（示例选择器）
        aluminum_row = None
        for row in price_table.select("tr"):
            if "铝" in row.text:
                aluminum_row = row
                break
        
        if not aluminum_row:
            raise ValueError("未找到铝价数据行")
        
        # 4. 提取价格数据
        cells = aluminum_row.select("td")
        product_name = cells[0].text.strip()
        price = cells[1].text.strip().replace(",", "")  # 移除数字千位分隔符
        unit = cells[2].text.strip()
        
        # 5. 构建数据结构
        data = {
            "product": product_name,
            "price": float(price),
            "unit": unit,
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "source": url
        }
        
        # 6. 保存JSON文件（GitHub Pages可访问路径）
        output_path = os.path.join("data", "aluminum_price.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已更新：{data}")
        return True

    except Exception as e:
        print(f"爬取失败：{str(e)}")
        return False

if __name__ == "__main__":
    crawl_aluminum_price()
