from fastapi import FastAPI, HTTPException, Query
import requests
from bs4 import BeautifulSoup
import random

app = FastAPI(title="Amazon Global Product Scraper API")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

@app.get("/scrape")
def scrape_amazon(url: str = Query(..., description="Amazon Ürün Detay Sayfası URL'si")):
    if "amazon." not in url:
        raise HTTPException(status_code=400, detail="Geçersiz Amazon URL'si")
        
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"status": "error", "message": f"Amazon engelledi veya sayfa bulunamadı. Kod: {response.status_code}"}
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Başlık Çıkarma
        title_el = soup.find("span", {"id": "productTitle"})
        title = title_el.get_text().strip() if title_el else "Bulunamadı"
        
        # Fiyat Çıkarma
        price_el = soup.find("span", {"class": "a-offscreen"})
        price = price_el.get_text().strip() if price_el else "Bulunamadı"
        
        # Stok Durumu Çıkarma
        availability_el = soup.find("div", {"id": "availability"})
        stock = "In Stock"
        if availability_el and "out of stock" in availability_el.get_text().lower():
            stock = "Out of Stock"
            
        # Puan Çıkarma
        rating_el = soup.find("span", {"class": "a-icon-alt"})
        rating = rating_el.get_text().strip() if rating_el else "Bulunamadı"
        
        return {
            "status": "success",
            "data": {
                "title": title,
                "price": price,
                "stock_status": stock,
                "rating": rating
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
