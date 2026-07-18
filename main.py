from fastapi import FastAPI, HTTPException, Query
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = FastAPI(title="Amazon Global Product Scraper API")

# ScraperAPI'den aldığın ücretsiz API anahtarını buraya yapıştır
SCRAPER_API_KEY = "BURAYA_KOPYALADIGIN_KEYI_YAZ"

@app.get("/scrape")
def scrape_amazon(url: str = Query(..., description="Amazon Ürün Detay Sayfası URL'si")):
    if "amazon." not in url:
        raise HTTPException(status_code=400, detail="Geçersiz Amazon URL'si")
        
    try:
        # url_encode işlemi yapıyoruz
        encoded_amazon_url = urllib.parse.quote_plus(url)
        
        # render=true diyerek ScraperAPI'ye arka planda gerçek Chrome tarayıcı açtırıyoruz
        proxy_url = f"https://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_amazon_url}&render=true"
        
        # Gerçek tarayıcı yüklendiği için timeout süresini biraz uzun tutuyoruz (20 saniye)
        response = requests.get(proxy_url, timeout=30)
        
        if response.status_code != 200:
            return {"status": "error", "message": f"Tarayıcı sunucusu hata döndürdü. Kod: {response.status_code}"}
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # # Başlık Çıkarma
        title_el = soup.find("span", {"id": "productTitle"})
        title = title_el.get_text().strip() if title_el else "Bulunamadı"
        
        # # Fiyat Çıkarma (Tarayıcı yüklendiği için artık bu etiket kesinlikle var)
        price = "Bulunamadı"
        price_span = soup.find("span", {"class": "a-price"})
        if price_span:
            offscreen = price_span.find("span", {"class": "a-offscreen"})
            if offscreen:
                price = offscreen.get_text().strip()
                
        if price == "Bulunamadı":
            whole = soup.find("span", {"class": "a-price-whole"})
            fraction = soup.find("span", {"class": "a-price-fraction"})
            if whole:
                whole_text = whole.get_text().strip().replace(",", "").replace(".", "")
                fraction_text = fraction.get_text().strip() if fraction else "00"
                price = f"{whole_text},{fraction_text} TL"
        
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
