import os
import requests

# Google AI Studio'dan aldığın ücretsiz API anahtarı başarıyla eklendi
GEMINI_API_KEY = "AIzaSyAe8Ww1ApeOxIumWUonsl5cqmlg0JcAtOM"

# ⚠️ BURAYA DÜNÜN ÇALIŞAN RENDER PROJE LİNKİNİ YAZ (Sonunda /scrape kalmalı)
MY_AMAZON_API_URL = "https://amazon-scraper-xyz.onrender.com/scrape"

def get_product_data(amazon_url: str):
    """Kendi yazdığımız API'den ürün bilgilerini çeker"""
    try:
        response = requests.get(MY_AMAZON_API_URL, params={"url": amazon_url}, timeout=35)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return result.get("data")
    except Exception as e:
        print(f"API'den veri çekilirken hata oluştu: {e}")
    return None

def generate_viral_script(product_title: str, price: str, rating: str):
    """Gemini AI kullanarak viral Instagram Reels senaryosu üretir"""
    
    prompt = f"""
    Sen profesyonel bir sosyal medya içerik üreticisisin ve Instagram Reels algoritmalarını çok iyi biliyorsun. 
    Sana verdiğim Amazon ürün bilgilerini kullanarak, izlenme süresini (watch time) tavan yaptıracak, merak uyandırıcı, 
    kancalı (hook) ve tamamen Türkçe bir viral video senaryosu yaz.

    Ürün Bilgileri:
    - Ürün Adı: {product_title}
    - Canlı Fiyatı: {price}
    - Kullanıcı Puanı: {rating}

    Senaryo Kuralları:
    1. İlk 3 saniyede izleyiciyi tutacak şok edici bir giriş (Hook) cümlesi olsun.
    2. Video kesinlikle dikey video formatına (Reels/TikTok) uygun, akıcı bir dille yazılmalı. Sakın yatay format düşünme.
    3. Metin içinde sahne geçişleri için [Ekranda ürünün görseli belirecek], [Fiyat grafiği gelecek] gibi yönetmen notları ekle.
    4. Videonun sonuna izleyicileri yorum yapmaya zorlayacak bir soru ekle (Örn: "Sizce bu fiyata değer mi? Yorumlara yazın, linki DM'den atayım").
    5. En alta da video için popüler 5 adet hashtag (#) ekle.
    """

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(gemini_url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            text_output = res_json['candidates'][0]['content']['parts'][0]['text']
            return text_output
        else:
            return f"Gemini API hatası oluştu. Kod: {response.status_code}"
    except Exception as e:
        return f"Yapay zeka tetiklenirken hata oluştu: {e}"

if __name__ == "__main__":
    # Test etmek için dün RapidAPI'de fiyatını başarıyla çektiğimiz Under Armour ayakkabı linki
    test_url = "https://www.amazon.com.tr/Under-Armour-Charged-Pursuit-Ayakkab%C4%B1%C4%B1s%C4%B1/dp/B0D1JLMJJM"
    
    print("🔄 1. Adım: Kendi Amazon API'mizden ürün verileri canlı olarak çekiliyor...")
    product = get_product_data(test_url)
    
    if product:
        print("✅ Veriler başarıyla alındı! Şimdi yapay zekaya viral senaryo yazdırılıyor...\n")
        print("-" * 50)
        
        viral_video_script = generate_viral_script(
            product_title=product.get("title"),
            price=product.get("price"),
            rating=product.get("rating")
        )
        
        print(viral_video_script)
        print("-" * 50)
    else:
        print("❌ Ürün verileri kendi API'nizden çekilemedi. Linki veya Render durumunu kontrol edin.")
