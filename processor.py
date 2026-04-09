import json

def process_data(items):
    """
    对采集到的数据进行清洗、去重、排序和性价比计算
    """
    # 1. 数据清洗与去重
    cleaned = []
    seen = set()
    for item in items:
        # 过滤无效数据
        if item.get('price') is None or not item.get('title'):
            continue
        
        # 强制类型转换
        try:
            item['price'] = float(item['price'])
            item['sales'] = int(item.get('sales', 0))
            item['rating'] = float(item.get('rating', 0.0))
        except (ValueError, TypeError):
            continue
            
        # 根据 url 或 id 去重
        key = item.get('url') or item.get('id')
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(item)
    
    if not cleaned:
        return []

    # 2. 提取特征边界值用于归一化
    prices = [x['price'] for x in cleaned]
    sales = [x['sales'] for x in cleaned]
    ratings = [x['rating'] for x in cleaned]
    
    min_p, max_p = min(prices), max(prices)
    min_s, max_s = min(sales), max(sales)
    min_r, max_r = min(ratings), max(ratings)
    
    # 3. 计算性价比得分
    # 逻辑：价格越低越好，销量和评分越高越好
    for item in cleaned:
        p = item['price']
        s = item['sales']
        r = item['rating']
        
        # 极差归一化 (0~1)
        np = (p - min_p) / (max_p - min_p) if max_p > min_p else 0.5
        ns = (s - min_s) / (max_s - min_s) if max_s > min_s else 0.5
        nr = (r - min_r) / (max_r - min_r) if max_r > min_r else 0.5
        
        # 综合得分 = 0.4*销量得分 + 0.4*评分得分 - 0.2*价格得分
        score = 0.4 * ns + 0.4 * nr - 0.2 * np
        item['score'] = round(score, 4)
        
    # 4. 标注性价比推荐 (前20%或至少1个)
    cleaned.sort(key=lambda x: x['score'], reverse=True)
    top_n = max(1, int(len(cleaned) * 0.2))
    for i, item in enumerate(cleaned):
        item['recommended'] = (i < top_n)
        
    # 5. 最终按价格从低到高排序返回
    cleaned.sort(key=lambda x: x['price'])
    
    return cleaned

if __name__ == "__main__":
    # 测试代码
    sample = [
        {"title": "商品A", "price": 100, "sales": 500, "rating": 4.5, "url": "a"},
        {"title": "商品B", "price": 90, "sales": 200, "rating": 4.0, "url": "b"},
        {"title": "商品C", "price": 110, "sales": 1000, "rating": 4.8, "url": "c"}
    ]
    print(json.dumps(process_data(sample), indent=2, ensure_ascii=False))
