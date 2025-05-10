from config import headers, baseUrls, useragents
from bs4 import BeautifulSoup
import requests
import json
import random

def get_listing_amazon(keyword):
    products_data = []
    final_url = baseUrls['amazon'] + keyword
    headers["User-Agent"] = useragents[random.randint(0,31)]
    response = requests.get(final_url, headers=headers, timeout=10)
    print(response.status_code)
    if response.status_code == 200:
        soup=BeautifulSoup(response.text,'html.parser')
        products = soup.find_all('div', {'data-component-type': 's-search-result'})
        print(products[0])
        for product in products:
            title_tag = product.find('h2', class_='a-size-base-plus a-spacing-none a-color-base a-text-normal')
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            price=product.find("span",{"class":"a-price"}).find("span").text
            price.replace(',', '') 
            # print(price)
            products_data.append({
                'title': title,
                'price': price.replace('\xa0', ' ')
            })
            # h2_elements = soup.find_all('h2', class_='a-size-base-plus a-spacing-none a-color-base a-text-normal')
            # titles = [h2.get_text(strip=True) for h2 in h2_elements]
            # for title in titles:
            #     print(title)
        
        
    # soup = BeautifulSoup(response.text, 'html.parser')
    # with open('scraped_data.txt', 'w', encoding='utf-8') as jsonfile:
    #     jsonfile.write(str(soup))
    # print(products_data)