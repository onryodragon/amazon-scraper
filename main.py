from fastapi import FastAPI, HTTPException, Query
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="Amazon Global Product Scraper API")

@app.get("/scrape")
def scrape_amazon(url: str = Query(..., description="Amazon Ürün Detay Sayfası URL'si")):
    if "amazon." not in url:
        raise HTTPException(status_code=400, detail="Geçersiz Amazon URL'si")
        
    # Amazon engelini otomatik aşan ücretsiz proxy köprüsü
    scraper_api_url = f"https://api.scraperapi.com/?api_key=5be8aefbf500f40d70b77a06f3bdf916&url={url}"
    
    try:
        # İstek doğrudan ScraperAPI üzerinden gidiyor, Amazon botu algılayamıyor
        response = requests.get(scraper_api_url, timeout=20)
        if response.status_code != 200:
            return {"status": "error", "message": f"Proxy sunucusu yanıt vermedi. Kod: {response.status_code}"}
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # # Başlık Çıkarma
        title_el = soup.find("span", {"id": "productTitle"})
        title = title_el.get_text().strip() if title_el else "Bulunamadı"
        
        # # Fiyat Çıkarma (Geliştirilmiş Kombinasyon)
        price = "Bulunamadı"
        
        # 1. Yöntem: Standart bütünleşik fiyat
        price_span = soup.find("span", {"class": "a-price"})
        if price_span:
            offscreen = price_span.find("span", {"class": "a-offscreen"})
            if offscreen:
                price = offscreen.get_text().strip()
        
        # 2. Yöntem: Amazon.com.tr tam ve kuruş etiketlerini birleştirme
        if price == "Bulunamadı":
            whole = soup.find("span", {"class": "a-price-whole"})
            fraction = soup.find("span", {"class": "a-price-fraction"})
            if whole:
                whole_text = whole.get_text().strip().replace(",", "").replace(".", "")
                fraction_text = fraction.get_text().strip() if fraction else "00"
                price = f"{whole_text},{fraction_text} TL"
                
        # 3. Yöntem: Alternatif fiyat alanı
        if price == "Bulunamadı":
            alt_price = soup.find("span", {"id": "priceblock_ourprice"}) or soup.find("span", {"id": "priceblock_dealprice"})
            if alt_price:
                price = alt_price.get_text().strip()
        
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
