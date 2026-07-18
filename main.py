from fastapi import FastAPI, HTTPException, Query
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

app = FastAPI(title="Amazon Global Product Scraper API")

@app.get("/scrape")
def scrape_amazon(url: str = Query(..., description="Amazon Ürün Detay Sayfası URL'si")):
    if "amazon." not in url:
        raise HTTPException(status_code=400, detail="Geçersiz Amazon URL'si")
        
    try:
        encoded_url = urllib.parse.quote_plus(url)
        google_proxy_url = f"https://translate.google.com/translate?sl=en&tl=tr&u={encoded_url}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(google_proxy_url, headers=headers, timeout=15)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        
        # # Başlık Çıkarma
        title_el = soup.find("span", {"id": "productTitle"})
        title = title_el.get_text().strip() if title_el else "Bulunamadı"
        
        # # Fiyat Çıkarma (Gelişmiş Seçiciler + Regex Kombinasyonu)
        price = "Bulunamadı"
        
        # 1. Klasik HTML Seçicileri Deneyelim
        price_span = soup.find("span", {"class": "a-price"})
        if price_span:
            offscreen = price_span.find("span", {"class": "a-offscreen"})
            if offscreen:
                price = offscreen.get_text().strip()
                
        if price == "Bulunamadı":
            color_price = soup.find("span", {"data-a-color": "price"}) or soup.find("span", {"class": "a-color-price"})
            if color_price:
                price = color_price.get_text().strip()

        # 2. JavaScript Bloklarından Regex ile Çekme (Kesin Çözüm)
        if price == "Bulunamadı" or price == "":
            # Sayfa içindeki fiyat kalıplarını ara (Örn: 1.250,00 TL veya 1250.00)
            price_match = re.search(r'"priceAmount"\s*:\s*([\d\.]+)', html_content)
            if price_match:
                price = f"{price_match.group(1)} TL"
            else:
                # Alternatif başka bir kalıp dene
                price_match_alt = re.search(r'"buyingPrice"\s*:\s*([\d\.]+)', html_content)
                if price_match_alt:
                    price = f"{price_match_alt.group(1)} TL"

        # # Stok Durumu Çıkarma
        availability_el = soup.find("div", {"id": "availability"})
        stock = "In Stock"
        if availability_el and "out of stock" in availability_el.get_text().lower():
            stock = "Out of Stock"
            
        # # Puan Çıkarma
        rating_el = soup.find("span", {"class": "a-icon-alt"})
        rating = rating_el.get_text().strip() if rating_el else "Bulunamadı"
        
        return {
            "status": "success",
            "data": {
                "title": title,
                "price": price if price != "Bulunamadı" else "",
                "stock_status": stock,
                "rating": rating
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
