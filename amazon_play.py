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

    # Scroll down to load all products
    for _ in range(5):  # Reduced scroll count for better performance
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)  # Reduced sleep time

    content = await page.content()
    
    soup = BeautifulSoup(
        content,
        "html.parser"
    )
    
    products = soup.find_all('div', {'data-component-type': 's-search-result'})
    
    for product in products:
        # Extract title
        title_tag = product.find('h2', class_='a-size-mini')
        if not title_tag:
            title_tag = product.find('h2', class_='a-size-base-plus')
        title = title_tag.get_text(strip=True) if title_tag else "No title"
        
        # Extract price
        price = product.find("span", {"class": "a-price"})
        price_span = price.find("span", {"class": "a-offscreen"}) if price else None
        price_value = price_span.get_text(strip=True) if price_span else '-1'
        
        # Extract product link
        link_tag = product.find('a', {'class': 'a-link-normal s-no-outline'})
        if not link_tag:
            link_tag = product.find('a', {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        relative_link = link_tag['href'] if link_tag else None
        product_link = f"https://www.amazon.ae{relative_link}" if relative_link else None
        
        # Extract image URL
        img_tag = product.find('img', {'class': 's-image'})
        img_url = img_tag['src'] if img_tag else None
        
        # Extract brand (can be in different places)
        brand = "No brand"
        # Try to find brand in different possible locations
        brand_span = product.find('span', {'class': 'a-size-base-plus'})
        if brand_span:
            brand = brand_span.get_text(strip=True)
        else:
            brand_div = product.find('div', {'class': 'a-row a-size-base a-color-secondary'})
            if brand_div:
                brand = brand_div.get_text(strip=True).split('by')[-1].strip()
        
        product_list.append({
            'title': title,
            'price': price_value.replace('\xa0', ' '),
            'link': product_link,
            'image_url': img_url,
            'brand': brand
        })
    return product_list


async def fetch_product_links(keywords):
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
        
        base_url = "https://www.amazon.ae/s?k=" + keywords.replace(' ', '+')
        final_data = await scrape_category(page, base_url)
        
        await browser.close()
        return final_data


# Example usage:
# final_product_list = asyncio.run(fetch_product_links("wireless headphones"))
# print(final_product_list)