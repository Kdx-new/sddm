import os
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone, timedelta

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
            # 3. 提取产品名称（精确匹配A00铝）
            product_tag = container.select_one("p:first-child a")
            if not product_tag:
                continue
                
            product = product_tag.text.strip()
            if "A00铝" not in product and "电解铝" not in product:
                continue
                
            # 4. 提取日期
            date_tag = container.select_one("p:first-child span")
            date_str = date_tag.text.strip() if date_tag else datetime.now().strftime("%m-%d")
            current_year = datetime.now().year
            full_date = f"{current_year}-{date_str}"
            
            # 5. 提取价格
            price_tag = container.select_one("p:nth-child(3) label.fluctuat_number")
            price = 0.0
            if price_tag:
                price_text = re.sub(r"[^\d.]", "", price_tag.text)
                try:
                    price = float(price_text) if price_text else 0.0
                except ValueError:
                    pass
            
            # 6. 提取单位
            unit_tag = price_tag.find_next_sibling("label") if price_tag else None
            unit = unit_tag.text.strip("()") if unit_tag else "元/吨"
            
            # 7. 提取涨跌值
            change_tag = container.select_one("p:nth-child(2) label:nth-child(2)")
            change = 0
            if change_tag:
                change_text = re.sub(r"[^\d\-+]", "", change_tag.text)
                try:
                    change = int(change_text) if change_text else 0
                except ValueError:
                    pass
            
            data_blocks.append({
                "product": "A00铝",  # 统一产品名称
                "date": full_date,
                "price": price,
                "unit": unit,
                "change": change
            })

        # 确保输出目录存在
        repo_root = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(repo_root, "aluminum_prices.json")
        
        # 历史数据处理逻辑 - 关键修复
        existing_data = {"data": []}
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    pass
        
        # 创建日期索引字典 - 确保每天只有一条最新数据
        date_index = {}
        for idx, item in enumerate(existing_data.get("data", [])):
            date_index[item["date"]] = idx
        
        # 合并数据 - 关键修复
        updated_data = existing_data.get("data", [])
        
        for new_item in data_blocks:
            # 如果已有同一天数据，则替换而非追加
            if new_item["date"] in date_index:
                updated_data[date_index[new_item["date"]]] = new_item
            else:
                updated_data.append(new_item)
                date_index[new_item["date"]] = len(updated_data) - 1
        
        # 按日期排序 - 确保数据顺序正确
        updated_data.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
        
        # 只保留最近7天的数据
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        updated_data = [item for item in updated_data if item["date"] >= seven_days_ago]
        
        # 保存结果
        result = {
            "source": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": updated_data
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 写入验证
        if os.path.exists(output_path):
            print(f"成功提取{len(data_blocks)}条数据 | 保存路径: {output_path}")
            return True
        else:
            raise Exception("文件写入失败")
        
    except Exception as e:
        print(f"爬取失败: {str(e)}")
        # 保存错误日志
        error_path = os.path.join(os.path.dirname(__file__), "error.log")
        with open(error_path, "a") as f:
            f.write(f"{datetime.now()}: Error - {str(e)}\n")
        return False

if __name__ == "__main__":
    print("开始铝价数据爬取...")
    if crawl_aluminum_data():
        print("数据更新成功")
    else:
        print("数据更新失败，请检查错误日志")
