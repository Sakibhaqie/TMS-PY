from config import headers_noon, baseUrls, useragents
from bs4 import BeautifulSoup
import requests
import json
import random

def get_pricing_noon(keyword): 
    products_data = []
    final_url = baseUrls['noon'] + keyword
    headers_noon["User-Agent"] = useragents[random.randint(0,31)]
    headers_noon["referer"] = final_url
    response = requests.get(final_url, headers=headers_noon, timeout=1000)
    print(response.status_code)
    print(final_url)
    
    
