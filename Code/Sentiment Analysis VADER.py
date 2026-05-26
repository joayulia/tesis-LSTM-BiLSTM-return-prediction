import re
import time
import os
import random
import pandas as pd
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import undetected_chromedriver as uc

vader = SentimentIntensityAnalyzer()
stock_lexicon = {
    'anjlok': -4.0, 'memerah': -3.5, 'terkoreksi': -2.0, 'loyo': -2.5,
    'ambruk': -4.0, 'melejit': 4.0, 'menguat': 3.0, 'meroket': 4.0,
    'borong': 3.0, 'cuan': 3.0, 'rebound': 3.0, 'net buy': 2.5,
    'net sell': -2.5, 'bullish': 3.5, 'bearish': -3.5
}
vader.lexicon.update(stock_lexicon)

lq45 = ['GoTo Gojek Tokopedia PT'] 
#lq45 = ['Sarana Menara Nusantara']
CHROME_VERSION = 147 

def get_browser():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = uc.Chrome(options=options, version_main=CHROME_VERSION)
    driver.set_page_load_timeout(120) # Timeout 2 menit
    return driver

def get_stocks():
    stocks = []
    driver = get_browser()
    main_url = 'https://id.investing.com/equities/indonesia'
    print(f"[*] Mengakses daftar saham: {main_url}")
    try:
        driver.get(main_url)
        time.sleep(15) 
        
        # Scroll
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Cari di dalam tabel harga
        table = soup.find('table')
        if not table:
            print("Tabel tidak ditemukan.")
            all_links = soup.find_all('a', href=True)
        else:
            all_links = table.find_all('a', href=True)

        for link in all_links:
            name = link.get_text(strip=True)
            href = link['href']
            if '/equities/' in href and any(lq.lower() in name.lower() for lq in lq45):
                if (name, href) not in stocks:
                    stocks.append((name, href))
                    print(f"    [+] Terdeteksi: {name}")
    except Exception as e:
        print(f"[!] Error ambil list saham: {e}")
    finally:
        driver.quit()
    return list(set(stocks))

def parse_date_flexible(text):
    text = text.lower()
    now = datetime.now()
    try:
        if any(x in text for x in ["menit", "jam", "detik", "lalu"]):
            return now
        if "kemarin" in text:
            return now - timedelta(days=1)
        
        match = re.search(r'(\d{1,2}\s+[a-z]+\s+\d{4})|(\d{1,2}[\./]\d{1,2}[\./]\d{4})', text)
        if match:
            return pd.to_datetime(match.group(0), dayfirst=True).to_pydatetime()
    except:
        pass
    return None

def get_news_research(stocks, total_pages=150):
    news_list = []
    start_date_limit = datetime(2020, 3, 1)
    
    for name, link in stocks:
        driver = get_browser()
        print(f"\n[*] MEMULAI RISET: {name}")
        try:
            target_link = link.rstrip('/')
            if not target_link.endswith('-news'):
                target_link = f"{target_link}-news"

            for page in range(1, total_pages + 1):
                url = f"https://id.investing.com{target_link}/{page}" if page > 1 else f"https://id.investing.com{target_link}"
                
                # Handling jika link sudah berisi domain
                if link.startswith('http'):
                    url = f"{target_link}/{page}" if page > 1 else target_link

                driver.get(url)
                time.sleep(random.uniform(10, 15))
                driver.execute_script("window.scrollTo(0, 500);")
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # Mencari link yang mengandung '/news/'
                potential_articles = soup.find_all('a', href=re.compile(r'/news/'))
                
                found_on_page = 0
                last_date = "N/A"

                for a_tag in potential_articles:
                    try:
                        headline = a_tag.get_text(strip=True)
                        if len(headline) < 30: continue
                        
                        parent = a_tag.find_parent(['div', 'article', 'li'])
                        news_date = None
                        if parent:
                            time_tag = parent.find('time')
                            if time_tag and time_tag.has_attr('datetime'):
                                news_date = pd.to_datetime(time_tag['datetime']).to_pydatetime()
                            else:
                                news_date = parse_date_flexible(parent.get_text(" ", strip=True))
                        
                        if not news_date:
                            news_date = parse_date_flexible(a_tag.get_text())

                        if not news_date: continue
                        news_date = news_date.replace(tzinfo=None)

                        if news_date < start_date_limit:
                            print(f"    [!] Batas 2020 tercapai ({news_date.date()}).")
                            return news_list

                        if not any(e[1] == headline for e in news_list):
                            news_list.append([name, headline, news_date])
                            found_on_page += 1
                            last_date = news_date.date()
                    except: continue
                
                print(f"    [+] Hal {page}: {found_on_page} berita. (Terakhir: {last_date})")
                if found_on_page == 0 and page > 1: break
                
        finally:
            driver.quit()
    return news_list

def preprocess_and_score(raw_data):
    df = pd.DataFrame(raw_data, columns=['Saham', 'Headline', 'Tanggal'])
    translator = GoogleTranslator(source='id', target='en')
    print("[*] Preprocessing & Scoring...")
    
    results = []
    for idx, row in df.iterrows():
        try:
            # Terjemahkan per kalimat
            translated = translator.translate(row['Headline'])
            score = vader.polarity_scores(translated)['compound']
        except:
            score = 0
        results.append({'Tanggal': row['Tanggal'], 'Saham': row['Saham'], 'Headline': row['Headline'], 'Score': score})
    return pd.DataFrame(results)

if __name__ == "__main__":
    print("=== START ===")
    
    # 1. Ambil list saham berdasarkan filter lq45
    list_saham = get_stocks()
    
    if list_saham:
        # 2. Proses Scraping Berita (Mundur sampai Maret 2020)
        data_berita = get_news_research(list_saham, total_pages=500)
        
        if data_berita:
            # 3. Preprocessing (Translate) & Sentiment Analysis (VADER)
            df_scored = preprocess_and_score(data_berita)
            
            # 4. Agregasi Harian (Gabung judul berita di tanggal yang sama)
            print("[*] Melakukan agregasi harian")
            df_scored['Tanggal'] = pd.to_datetime(df_scored['Tanggal']).dt.date
            df_agregat = df_scored.groupby(['Tanggal', 'Saham']).agg({
                'Score': 'mean', 
                'Headline': ' | '.join
            }).reset_index()
            
            # 5. Penanganan Tanggal Kosong & Sinkronisasi Hari Bursa
            print("[*] Sinkronisasi Tanggal...")
            
            start_date = "2020-03-01"
            end_date = "2026-03-31"
            date_range = pd.date_range(start=start_date, end=end_date)
            
            final_list = []
            
            for s in df_agregat['Saham'].unique():
                # Filter data per saham
                temp = df_agregat[df_agregat['Saham'] == s].copy()
                temp['Tanggal'] = pd.to_datetime(temp['Tanggal'])
                temp = temp.set_index('Tanggal')
                
                # Masukkan tanggal yang bolong
                temp = temp.reindex(date_range)
                temp['Saham'] = s
                
                temp['Score'] = temp['Score'].ffill().fillna(0)
                temp['Headline'] = temp['Headline'].fillna("No News")
                
                temp = temp[temp.index.dayofweek < 5] # 0=Senin, 4=Jumat
                
                final_list.append(temp)
            
            # 6. Gabungkan semua dan Simpan ke Excel
            df_final = pd.concat(final_list).reset_index().rename(columns={'index': 'Tanggal'})
            df_final = df_final.sort_values(by=['Saham', 'Tanggal'], ascending=[True, False])
            
            timestamp = time.strftime('%Y%m%d_%H%M')
            nama_file = f"DATA_SENTIMEN_{timestamp}.xlsx"
            
            df_final.to_excel(nama_file, index=False)
            
            print(f"Berhasil")
        else:
            print("Gagal, tidak ada data berita yang berhasil di-scrape.")
    else:
        print("Gagal, saham tidak ditemukan.")