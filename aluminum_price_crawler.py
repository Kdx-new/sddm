import os
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone

def crawl_aluminum_data():
    url = "https://www.ccmn.cn/priceinfo/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.ccmn.cn/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    try:
        # 1. 获取页面内容
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 2. 定位所有产品容器
        data_blocks = []
        containers = soup.select("div.fluctuat_content")
        
        for container in containers:
            # 3. 提取产品名称（精确匹配铝产品）
            product_tag = container.select_one("p:first-child a")
            if not product_tag:
                continue
                
            product = product_tag.text.strip()
            # 过滤非铝产品（A00铝、铝合金等）
            if "铝" not in product and "铝合金" not in product:
                continue
                
            # 4. 提取日期
            date_tag = container.select_one("p:first-child span")
            date_str = date_tag.text.strip() if date_tag else datetime.now().strftime("%m-%d")
            
            # 5. 提取价格（关键修复） - 第三个<p>的第一个label
            price_tag = container.select_one("p:nth-child(3) label.fluctuat_number")
            price = 0.0
            if price_tag:
                # 清洗价格数据（移除逗号和非数字字符）
                price_text = re.sub(r"[^\d.]", "", price_tag.text)
                try:
                    price = float(price_text) if price_text else 0.0
                except ValueError:
                    pass
            
            # 6. 提取单位 - 价格标签后的第一个label
            unit_tag = price_tag.find_next_sibling("label") if price_tag else None
            unit = unit_tag.text.strip("()") if unit_tag else "元/吨"
            
            # 7. 提取涨跌值（关键修复） - 第二个<p>的第二个label
            change_tag = container.select_one("p:nth-child(2) label:nth-child(2)")
            change = 0
            if change_tag:
                # 清洗涨跌值（移除空格等非数字字符）
                change_text = re.sub(r"[^\d\-+]", "", change_tag.text)
                try:
                    change = int(change_text) if change_text else 0
                except ValueError:
                    pass
            
            data_blocks.append({
                "product": product,
                "date": f"2025-{date_str}",
                "price": price,
                "unit": unit,
                "change": change
            })

        # 确保输出目录存在
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "aluminum_prices.json")
        
        # 保存结果
        result = {
            "source": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data_blocks
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"成功提取{len(data_blocks)}条价格数据，保存至: {output_path}")
        return True
        
    except Exception as e:
        print(f"爬取失败: {str(e)}")
        # 保存原始HTML供调试
        debug_path = os.path.join(os.path.dirname(__file__), "error.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(response.text if 'response' in locals() else "无响应")
        print(f"调试信息已保存至: {debug_path}")

if __name__ == "__main__":
    if crawl_aluminum_data():
        print("数据更新成功")
    else:
        print("数据更新失败，请检查错误日志")
