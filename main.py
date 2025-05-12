# server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
from lulu import fetch_product_links as fetch1
from amazon_play import fetch_product_links as fetch2
from openai import OpenAI
from dotenv import load_dotenv
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# ——— CONFIG ———
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

# ——— FASTAPI APP SETUP ———
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ——— MODELS ———
class SearchRequest(BaseModel):
    keyword: str

class ProductMatch(BaseModel):
    source: str
    title: str
    price: str
    link: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None

# ——— ROUTES ———
@app.post("/search", response_model=List[ProductMatch])
async def search_products(req: SearchRequest):
    keyword = req.keyword

    try:
        # Run both fetches in parallel
        lulu_products, amazon_products = await asyncio.gather(
            fetch1(keyword),
            fetch2(keyword)
        )

        combined = {"lulu": lulu_products, "amazon": amazon_products}

        print("done scrapping")
        # Use background thread for blocking OpenAI call
        completion = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You’re a product-comparison assistant. Input is a dict with keys 'lulu' and 'amazon', "
                        "each mapping to a list of {title, price} objects. Given the search keyword, "
                        "return the top 3 most relevant products from both sources. "
                        "Output a valid JSON array of objects. Each object must include: "
                        "source, title, price, link (optional), brand (optional), image_url (optional)."
                        "Output a **valid JSON array** of objects : "
                        "[{\"source\": \"lulu\"|\"amazon\", \"title\": \"…\", \"price\": \"…\"}, …] and nothing else. "
                        "Return ONLY a raw JSON array (double quotes, no Markdown, no explanation)."
                    )
                },
                {"role": "user", "content": f"Keyword: '{keyword}'\nProducts:\n{combined}"}
            ]
        )

        content_str = completion.choices[0].message.content.strip()
        product_list = json.loads(content_str)
        return product_list

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON returned from OpenAI: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ——— MAIN ENTRY POINT ———
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
