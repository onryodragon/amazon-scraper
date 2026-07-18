from fastapi import FastAPI, HTTPException, Query
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = FastAPI(title="Amazon Global Product Scraper API")

# ScraperAPI'den aldığın ücretsiz API anahtarını buraya yapıştır
SCRAPER_API_KEY = "BURAYA_GERÇEK_SCRAPERAPI_ANAHTARINI_YAPIŞTIR"

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
@app.get("/viral-senaryo")
def get_viral_script(url: str):
    product_data = scrape_amazon(url) 
    
    if not product_data:
        return {"status": "error", "message": "Ürün verileri çekilemedi."}
    
    # Verileri güvenli bir şekilde alıyoruz
    title = product_data.get("title", "Harika Ürün")
    price = product_data.get("price", "Fiyat Detayı İçin Tıklayın")
    rating = product_data.get("rating", "4.5")

    # Gemini API Ayarları
    gemini_key = "AQ.Ab8RN6KLUZFNX9ztEzMV8m0OT-PjVSxR7fUjZ0LppasB0-KXFQ"
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    
    prompt = f"""
    Sen profesyonel bir sosyal medya içerik üreticisisin ve Instagram Reels algoritmalarını çok iyi biliyorsun. 
    Sana verdiğim Amazon ürün bilgilerini kullanarak, izlenme süresini (watch time) tavan yaptıracak, merak uyandırıcı, 
    kancalı (hook) ve tamamen Türkçe bir viral video senaryosu yaz.

    Ürün Bilgileri:
    - Ürün Adı: {title}
    - Canlı Fiyatı: {price}
    - Kullanıcı Puanı: {rating}

    Senaryo Kuralları:
    1. İlk 3 saniyede izleyiciyi tutacak şok edici bir giriş (Hook) cümlesi olsun.
    2. Video kesinlikle dikey video formatına (Reels/TikTok) uygun, akıcı bir dille yazılmalı.
    3. Metin içinde sahne geçişleri için [Ekranda ürünün görseli belirecek], [Fiyat grafiği gelecek] gibi yönetmen notları ekle.
    4. Videonun sonuna izleyicileri yorum yapmaya zorlayacak bir soru ekle.
    5. En alta da video için popüler 5 adet hashtag (#) ekle.
    """

    import requests
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(gemini_url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            text_output = response.json()['candidates'][0]['content']['parts'][0]['text']
            return {"status": "success", "viral_script": text_output}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    return {"status": "error", "message": "Yapay zeka yanıt vermedi."}
