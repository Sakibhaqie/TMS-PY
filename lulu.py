import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from config import useragents

async def scrape_category(page, url):
    print("begin scrape")
    product_list = []
    await page.goto(
            url, 
            wait_until="load", 
            timeout=200000
        )
    await page.wait_for_load_state(
            "domcontentloaded"
        )
    await asyncio.sleep(2)
        # Scroll down to load all products
    # for _ in range(10):
    #     await page.evaluate(
    #         "window.scrollTo(0, document.body.scrollHeight)"
    #     )
    #     await asyncio.sleep(2)

    content = await page.content()
    
    soup = BeautifulSoup(
        content,
        "html.parser"
    )
    
    # print(soup)
    pattern = re.compile(r"^rounded-\[32px\] border border-\[#d9d9d9\]")

    products = soup.find_all("div", class_=pattern)

    
    # print(soup)
    # products = soup.find_all('div', class_= re.compile('rounded-[32px] border border-[#d9d9d9]'))
    print(len(products))
    for product in products:
        pattern2 = re.compile(r'^h-20 py-1 font-sans text-sm font-medium leading-\[1\.71\]')
        title_tag = product.find('a', class_=pattern2)
        title = title_tag.get_text(strip=True) if title_tag else "No title"
        price=product.find("span",attrs={"data-testid":"product-price"})
        product_list.append({
            'title': title,
            'price': price.text.strip()
        })
        # print(title)
        # print(price.text.strip())
    return product_list

async def fetch_product_links(keyword):
    """
    Main function to scrape product links from all categories.

    This function:
    - Reads category URLs from a file.
    - Launches a Chromium browser instance using Playwright.
    - Sets custom HTTP headers for better request handling.
    - Iterates through each category URL and scrapes product links.
    - Stores extracted product links in an SQLite database.
    - Ensures proper cleanup by closing database connections 
      and the browser after execution.

    Returns:
    - None (Results are stored in the database).
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.set_extra_http_headers({
            "User-Agent": useragents[random.randint(0,30)],
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        
        base_url = "https://gcc.luluhypermarket.com/en-ae/list/?search_text=" + keyword
        final_data = await scrape_category(page, base_url)
        
        # conn.close()
        await browser.close()
        return final_data
        

# final_product_list = asyncio.run(fetch_product_links("wireless"))
# print(final_product_list)