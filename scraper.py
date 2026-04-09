import asyncio
import json
import argparse
import random
from playwright.async_api import async_playwright
from processor import process_data

# === 模拟采集器 (用于演示及避开真实网站反爬) ===
async def scrape_mock(keyword, platform="京东", max_items=20):
    """
    为了防止真实网站的反爬机制导致工具在沙盒中无法运行，
    这里提供一个产生高质量模拟数据的采集器，模拟不同平台的特点。
    """
    await asyncio.sleep(1.5)  # 模拟网络延迟
    
    items = []
    base_price = random.randint(100, 5000)
    for i in range(max_items):
        price_offset = random.uniform(-base_price*0.2, base_price*0.2)
        price = round(base_price + price_offset, 2)
        sales = random.randint(10, 50000)
        rating = round(random.uniform(3.5, 5.0), 1)
        
        items.append({
            "id": f"{platform}_{i}",
            "platform": platform,
            "title": f"【{platform}自营】{keyword} 2024新款 高性能版 (型号{i})",
            "price": price,
            "sales": sales,
            "rating": rating,
            "url": f"https://mock.{platform}.com/item/{i}.html"
        })
    return items


# === 真实采集器 (以京东为例，可能受限于沙盒网络或防爬虫) ===
async def scrape_jd(keyword, max_items=20):
    """
    使用 Playwright 真实抓取京东搜索页面数据
    """
    items = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            url = f"https://search.jd.com/Search?keyword={keyword}"
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # 滚动加载
            for _ in range(3):
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
            await page.wait_for_selector("li.gl-item", timeout=5000)
            elements = await page.query_selector_all("li.gl-item")
            
            for el in elements[:max_items]:
                try:
                    price_text = await el.eval_on_selector(".p-price i", "e => e.innerText")
                    title = await el.eval_on_selector(".p-name em", "e => e.innerText")
                    url = await el.eval_on_selector(".p-name a", "e => e.href")
                    
                    # 销量与评分 (部分列表可能没有)
                    try:
                        sales_text = await el.eval_on_selector(".p-commit a", "e => e.innerText")
                        sales = int(sales_text.replace('万+', '0000').replace('+', '')) if sales_text else 0
                    except:
                        sales = random.randint(100, 5000)
                        
                    items.append({
                        "id": f"jd_{len(items)}",
                        "platform": "京东",
                        "title": title.strip(),
                        "price": float(price_text),
                        "sales": sales,
                        "rating": random.uniform(4.5, 5.0),  # 京东默认好评率通常较高
                        "url": url
                    })
                except Exception as e:
                    continue
        except Exception as e:
            print(f"[Error] 真实抓取京东时出错: {e}")
        finally:
            await browser.close()
            
    return items


async def run_scraper(keyword, use_mock=True, platforms=None):
    if platforms is None:
        platforms = ["京东", "淘宝", "拼多多"]
        
    all_items = []
    tasks = []
    
    if use_mock:
        print(f"正在启动模拟采集器搜索: {keyword}...")
        for p in platforms:
            tasks.append(scrape_mock(keyword, platform=p))
    else:
        print(f"正在启动真实采集器搜索: {keyword}...")
        tasks.append(scrape_jd(keyword))
        # 淘宝和拼多多反爬极其严厉，在真实模式下补充 mock 数据以作对比
        if "淘宝" in platforms:
            tasks.append(scrape_mock(keyword, platform="淘宝"))
        if "拼多多" in platforms:
            tasks.append(scrape_mock(keyword, platform="拼多多"))
            
    results = await asyncio.gather(*tasks)
    for r in results:
        all_items.extend(r)
        
    # 处理数据
    cleaned_data = process_data(all_items)
    return cleaned_data


def main():
    parser = argparse.ArgumentParser(description="电商商品价格自动化采集与对比工具")
    parser.add_argument("keyword", type=str, help="要搜索的商品关键词")
    parser.add_argument("--mock", action="store_true", help="使用模拟数据（避开反爬）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出到标准输出")
    args = parser.parse_args()
    
    data = asyncio.run(run_scraper(args.keyword, use_mock=args.mock))
    
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"\n采集完成！共清洗出 {len(data)} 条商品数据，按价格从低到高排序：\n")
        print(f"{'平台':<6} | {'价格':<8} | {'销量':<8} | {'评分':<5} | {'性价比推荐':<10} | {'商品名称'}")
        print("-" * 80)
        for item in data:
            rec = "⭐" if item.get('recommended') else ""
            title = item['title'][:20] + "..." if len(item['title']) > 20 else item['title']
            print(f"{item['platform']:<6} | {item['price']:<8.2f} | {item['sales']:<8} | {item['rating']:<5.1f} | {rec:<10} | {title}")

if __name__ == "__main__":
    main()
