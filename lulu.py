import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from config import useragents

async def scrape_category(page, url):
    print("Begin scraping Lulu Hypermarket")
    product_list = []
    
    await page.goto(
        url, 
        wait_until="load", 
        timeout=200000
    )
    await page.wait_for_load_state("domcontentloaded")
    
    # Scroll down to load more products (adjust range as needed)
    for _ in range(3):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)
    
    content = await page.content()
    soup = BeautifulSoup(content, "html.parser")
    
    # Find all product containers
    products = soup.find_all("div", class_=re.compile(r"rounded-\[32px\] border border-\[#d9d9d9\]"))
    print(f"Found {len(products)} products")
    
    for product in products:
        # Extract title
        title_tag = product.find("a", class_=re.compile(r"h-20 py-1 font-sans text-sm font-medium leading-\[1\.71\]"))
        title = title_tag.get_text(strip=True) if title_tag else "No title"
        
        # Extract price
        price_tag = product.find("span", attrs={"data-testid": "product-price"})
        price = price_tag.get_text(strip=True) if price_tag else "Price not available"
        
        # Extract product link
        link_tag = product.find("a", href=True)
        product_link = urljoin("https://gcc.luluhypermarket.com", link_tag["href"]) if link_tag else None
        
        # Extract image URL
        # img_tag = product.find("img", attrs={"id": "product-detail-image"})
        # img_url = img_tag["src"] if img_tag else None

        # Extract image URL from the tag with class "object-contain"
        img_tag = product.find("img", class_=lambda x: x and "object-contain" in x)

        # Default to None if tag isn't found
        img_url = None

        if img_tag:
            if img_tag.has_attr("srcset"):
                # Take the largest resolution from srcset (last item)
                srcset_parts = img_tag["srcset"].split(",")
                largest_image = srcset_parts[-1].strip().split(" ")[0]
                img_url = largest_image
            elif img_tag.has_attr("src"):
                # Fallback to src
                img_url = img_tag["src"]

        
        # Extract brand (may need adjustment based on actual HTML structure)
        brand_tag = product.find("div", class_=re.compile(r"text-\[12px\] font-normal leading-\[1\.5\] text-\[\#6d6d6d\]"))
        brand = brand_tag.get_text(strip=True) if brand_tag else "Brand not specified"
        
        product_list.append({
            'title': title,
            'price': price,
            'link': product_link,
            'image_url': img_url,
            'brand': brand
        })
    
    return product_list

async def fetch_product_links(keyword):
    """
    Main function to scrape product data from Lulu Hypermarket.
    
    Args:
        keyword (str): Search term for products
        
    Returns:
        list: List of dictionaries containing product information
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Set random user agent
        await page.set_extra_http_headers({
            "User-Agent": useragents[random.randint(0, len(useragents)-1)],
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        
        # Encode keyword for URL
        search_term = keyword.replace(" ", "+")
        base_url = f"https://gcc.luluhypermarket.com/en-ae/list/?search_text={search_term}"
        
        try:
            final_data = await scrape_category(page, base_url)
        except Exception as e:
            print(f"Error during scraping: {e}")
            final_data = []
        finally:
            await context.close()
            await browser.close()
        
        return final_data

# Example usage:
# final_product_list = asyncio.run(fetch_product_links("wireless headphones"))
# print(final_product_list)