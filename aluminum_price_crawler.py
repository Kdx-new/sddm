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
        response = requests.get(url, headers=headers, timeout=25)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 2. 定位所有产品容器 - 更稳健的选择器
        data_blocks = []
        containers = soup.select("div.fluctuat_content")
        
        if not containers:
            print("警告：未找到价格容器，网站结构可能已变更")
            # 保存原始HTML供调试
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
        
        for container in containers:
            try:
                # 3. 产品名称（更宽松的匹配）
                product_tag = container.select_one("p a")
                if not product_tag:
                    continue
                    
                product = product_tag.text.strip()
                
                # 4. 日期处理
                date_tag = container.select_one("p span")
                date_str = date_tag.text.strip() if date_tag else datetime.now().strftime("%m-%d")
                current_year = datetime.now().year
                
                # 5. 价格提取（更健壮的解析）
                price_tag = container.select_one("label.fluctuat_number")
                price = 0.0
                if price_tag:
                    price_text = re.search(r"[\d,]+\.?\d*", price_tag.text)
                    if price_text:
                        try:
                            price = float(price_text.group().replace(",", ""))
                        except ValueError:
                            pass
                
                # 6. 单位提取
                unit = "元/吨"  # 默认值
                unit_tags = container.select("label")
                if len(unit_tags) > 1:
                    unit_text = unit_tags[1].text.strip()
                    if unit_text and "元" in unit_text:
                        unit = unit_text.strip("()")
                
                # 7. 涨跌值（更健壮的解析）
                change = 0
                change_tag = container.select_one("label.fluctuat_range")
                if change_tag:
                    change_text = re.search(r"[-+]?\d+", change_tag.text)
                    if change_text:
                        try:
                            change = int(change_text.group())
                        except ValueError:
                            pass
                
                data_blocks.append({
                    "product": product,
                    "date": f"{current_year}-{date_str}",
                    "price": price,
                    "unit": unit,
                    "change": change
                })
                
            except Exception as e:
                print(f"处理容器时出错: {str(e)}")
                continue
        
        # 8. 确保输出目录存在
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "aluminum_prices.json")
        
        # 9. 保存结果（使用绝对路径）
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
        return False

if __name__ == "__main__":
    if crawl_aluminum_data():
        print("数据更新成功")
    else:
        print("数据更新失败，请检查错误日志")
