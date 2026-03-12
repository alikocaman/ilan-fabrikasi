"""
Akıllı İlan Fabrikası - Emlakçılar için AI Destekli İlan Üretim Sistemi
Full-Stack Python/Streamlit Uygulaması
"""

import streamlit as st
import sqlite3
import json
import os
import re
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# SAYFA AYARLARI (En üstte olmalı)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Akıllı İlan Fabrikası",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# BAĞIMLILIKLAR (Opsiyonel import'lar)
# ─────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env yoksa devam et

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Claude için sadece requests yeterli (built-in)
import urllib.request

# ─────────────────────────────────────────────
# MOBİL-ÖNCELİKLİ CSS
# ─────────────────────────────────────────────
MOBILE_CSS = """
<style>
  /* ── Temel Reset ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  html, body, [data-testid="stAppViewContainer"] {
      font-family: 'Inter', sans-serif !important;
      background: #0f0f14 !important;
      color: #e8e8ef !important;
  }

  /* ── Header Gradient ── */
  .app-header {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      border-radius: 20px;
      padding: 28px 24px 20px;
      margin-bottom: 24px;
      border: 1px solid rgba(99,179,237,0.15);
      text-align: center;
      position: relative;
      overflow: hidden;
  }
  .app-header::before {
      content: '';
      position: absolute; top: -50%; left: -50%;
      width: 200%; height: 200%;
      background: radial-gradient(circle at 60% 40%, rgba(99,179,237,0.08) 0%, transparent 60%);
      pointer-events: none;
  }
  .app-header h1 {
      font-size: clamp(22px, 5vw, 32px);
      font-weight: 800;
      background: linear-gradient(135deg, #63b3ed, #90cdf4, #ebf8ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin: 0 0 6px;
  }
  .app-header p {
      color: #94a3b8;
      font-size: 13px;
      margin: 0;
  }

  /* ── Kartlar ── */
  .card {
      background: #1a1a2e;
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 16px;
      border: 1px solid rgba(99,179,237,0.12);
      transition: border-color 0.2s;
  }
  .card:hover { border-color: rgba(99,179,237,0.3); }

  .card-title {
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: #63b3ed;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
  }

  /* ── Çıktı Metin Alanı ── */
  .output-box {
      background: #0f172a;
      border-radius: 12px;
      padding: 16px;
      font-size: 14px;
      line-height: 1.7;
      color: #cbd5e1;
      border: 1px solid rgba(99,179,237,0.1);
      white-space: pre-wrap;
      word-break: break-word;
      min-height: 80px;
  }

  /* ── Büyük Üret Butonu ── */
  .stButton > button[kind="primary"] {
      background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
      color: white !important;
      font-size: 18px !important;
      font-weight: 700 !important;
      border-radius: 14px !important;
      padding: 18px 24px !important;
      border: none !important;
      width: 100% !important;
      letter-spacing: 0.3px;
      box-shadow: 0 4px 20px rgba(37,99,235,0.4) !important;
      transition: all 0.2s !important;
  }
  .stButton > button[kind="primary"]:hover {
      transform: translateY(-2px) !important;
      box-shadow: 0 8px 28px rgba(37,99,235,0.5) !important;
  }

  /* ── Sekme Stili ── */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
      background: #0f172a;
      border-radius: 12px;
      padding: 4px;
      gap: 4px;
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
      border-radius: 8px !important;
      color: #94a3b8 !important;
      font-size: 13px !important;
      font-weight: 600 !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
      background: #2563eb !important;
      color: white !important;
  }

  /* ── Form Elemanları ── */
  [data-testid="stTextArea"] textarea,
  [data-testid="stTextInput"] input {
      background: #0f172a !important;
      border: 1.5px solid rgba(99,179,237,0.2) !important;
      border-radius: 12px !important;
      color: #e2e8f0 !important;
      font-size: 15px !important;
      padding: 14px !important;
  }
  [data-testid="stTextArea"] textarea:focus,
  [data-testid="stTextInput"] input:focus {
      border-color: #2563eb !important;
      box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
  }

  [data-testid="stSelectbox"] > div > div {
      background: #0f172a !important;
      border: 1.5px solid rgba(99,179,237,0.2) !important;
      border-radius: 12px !important;
      color: #e2e8f0 !important;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
      background: #1a1a2e !important;
  }

  /* ── Bilgi Kutucukları ── */
  .pdr-badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      margin: 3px 2px;
  }
  .badge-p { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
  .badge-d { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
  .badge-r { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }

  /* ── Profil Skoru ── */
  .profile-score {
      background: linear-gradient(135deg, #064e3b, #065f46);
      border-radius: 12px;
      padding: 12px 16px;
      border: 1px solid rgba(16,185,129,0.3);
      margin-bottom: 10px;
  }

  /* ── İkon Butonları ── */
  .stButton > button {
      border-radius: 10px !important;
      font-weight: 600 !important;
      transition: all 0.15s !important;
  }

  /* ── Divider ── */
  hr { border-color: rgba(99,179,237,0.1) !important; }

  /* ── Gizle gereksiz elementleri ── */
  #MainMenu, footer { visibility: hidden; }
  [data-testid="stDecoration"] { display: none; }

  /* ── Mobil padding azalt ── */
  .block-container { padding: 1rem 1rem 2rem !important; max-width: 680px !important; }

  /* ── Snackbar benzeri ── */
  .copy-success {
      background: rgba(16,185,129,0.15);
      border: 1px solid rgba(16,185,129,0.4);
      border-radius: 8px;
      padding: 8px 14px;
      color: #34d399;
      font-size: 13px;
      text-align: center;
  }

  /* ── Loading spinner ── */
  [data-testid="stSpinner"] { color: #63b3ed !important; }
</style>
"""

# ─────────────────────────────────────────────
# VERİTABANI KATMANI
# ─────────────────────────────────────────────

DB_PATH = "emlak_veritabani.db"

def init_db():
    """Veritabanını başlat, tabloları oluştur."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS ilanlar (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih       TEXT,
            ham_veri    TEXT,
            pdr_analizi TEXT,
            portal_metni TEXT,
            whatsapp_metni TEXT,
            instagram_metni TEXT,
            hedef_kitle TEXT,
            emlakci_id  TEXT DEFAULT 'varsayilan'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS geri_bildirimler (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ilan_id         INTEGER,
            metin_turu      TEXT,
            orijinal_metin  TEXT,
            duzeltilmis_metin TEXT,
            begeni          INTEGER DEFAULT 0,
            tarih           TEXT,
            emlakci_id      TEXT DEFAULT 'varsayilan',
            FOREIGN KEY (ilan_id) REFERENCES ilanlar(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS emlakci_profil (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            emlakci_id      TEXT UNIQUE,
            ad_soyad        TEXT,
            stil            TEXT DEFAULT 'dengeli',
            ortalama_metin_uzunlugu INTEGER DEFAULT 200,
            tercih_edilen_kelimeler TEXT DEFAULT '[]',
            kacinilankelimeler TEXT DEFAULT '[]',
            toplam_ilan     INTEGER DEFAULT 0,
            son_guncelleme  TEXT
        )
    """)

    conn.commit()
    conn.close()

def kaydet_ilan(ham_veri, pdr, portal, whatsapp, instagram, hedef_kitle, emlakci_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO ilanlar
          (tarih, ham_veri, pdr_analizi, portal_metni, whatsapp_metni, instagram_metni, hedef_kitle, emlakci_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), ham_veri, json.dumps(pdr, ensure_ascii=False),
          portal, whatsapp, instagram, hedef_kitle, emlakci_id))
    ilan_id = c.lastrowid
    conn.commit()
    conn.close()
    return ilan_id

def kaydet_geri_bildirim(ilan_id, metin_turu, orijinal, duzeltilmis, begeni, emlakci_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO geri_bildirimler
          (ilan_id, metin_turu, orijinal_metin, duzeltilmis_metin, begeni, tarih, emlakci_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ilan_id, metin_turu, orijinal, duzeltilmis, begeni, datetime.now().isoformat(), emlakci_id))
    conn.commit()
    conn.close()
    _profil_guncelle(emlakci_id, duzeltilmis)

def _profil_guncelle(emlakci_id, metin):
    """Kullanıcı düzeltmelerinden stil analizi yap ve profili güncelle."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Mevcut profili al
    c.execute("SELECT * FROM emlakci_profil WHERE emlakci_id = ?", (emlakci_id,))
    profil = c.fetchone()

    # Kelime analizi: sık kullanılan anlamlı kelimeler
    kelimeler = re.findall(r'\b[a-zA-ZğüşıöçĞÜŞİÖÇ]{4,}\b', metin.lower())
    stopwords = {"olan", "için", "ile", "veya", "gibi", "kadar", "daha", "çok",
                 "bunu", "evet", "hayır", "tamam", "değil", "olur", "olarak"}
    anlamli = [k for k in kelimeler if k not in stopwords]

    if profil:
        mevcut_kelimeler = json.loads(profil[6] or '[]')
        mevcut_kelimeler.extend(anlamli[:5])
        # En çok tekrar edilen 20 kelimeyi tut
        from collections import Counter
        top_20 = [k for k, _ in Counter(mevcut_kelimeler).most_common(20)]
        uzunluk = len(metin)
        yeni_uzunluk = int((profil[5] + uzunluk) / 2)

        # Stil tahmini: kısa metin → esnaf, uzun → kurumsal
        if yeni_uzunluk < 120:
            stil = 'esnaf'
        elif yeni_uzunluk > 280:
            stil = 'kurumsal'
        else:
            stil = 'dengeli'

        c.execute("""
            UPDATE emlakci_profil
            SET tercih_edilen_kelimeler=?, ortalama_metin_uzunlugu=?,
                stil=?, toplam_ilan=toplam_ilan+1, son_guncelleme=?
            WHERE emlakci_id=?
        """, (json.dumps(top_20, ensure_ascii=False), yeni_uzunluk,
              stil, datetime.now().isoformat(), emlakci_id))
    else:
        c.execute("""
            INSERT INTO emlakci_profil
              (emlakci_id, ad_soyad, stil, ortalama_metin_uzunlugu,
               tercih_edilen_kelimeler, toplam_ilan, son_guncelleme)
            VALUES (?, ?, 'dengeli', ?, ?, 1, ?)
        """, (emlakci_id, emlakci_id, len(metin),
              json.dumps(anlamli[:10], ensure_ascii=False), datetime.now().isoformat()))

    conn.commit()
    conn.close()

def profil_getir(emlakci_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM emlakci_profil WHERE emlakci_id = ?", (emlakci_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "emlakci_id": row[1], "ad_soyad": row[2], "stil": row[3],
            "uzunluk": row[4], "kelimeler": json.loads(row[5] or '[]'),
            "toplam_ilan": row[7]
        }
    return None

def son_ilanlar_getir(emlakci_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, tarih, ham_veri, hedef_kitle FROM ilanlar
        WHERE emlakci_id = ? ORDER BY id DESC LIMIT ?
    """, (emlakci_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────────
# ZEKA KATMANI — PDR ANALİZİ + PROMPT
# ─────────────────────────────────────────────

def pdr_analizi_yap(ham_veri: str) -> dict:
    """
    Ham metinden PDR (Problem-İhtiyaç-Risk) analizi çıkar.
    Kural tabanlı hızlı analiz (LLM API'sinden önce).
    """
    metin = ham_veri.lower()

    # PROBLEM / FIRSAT tespiti
    problem_ipuclari = {
        "eski bina": "Köklü yapısını modern konfor ile birleştiriyor",
        "1. kat": "Bahçeye yakın, engelsiz erişim avantajı",
        "bodrum": "Depolama ve yatırım potansiyeli olan katman",
        "bakımsız": "Kendi zevkinize göre şekillendirebileceğiniz ham elmas",
        "gürültülü": "Şehir merkezinin nabzında, ulaşım kolaylığı",
        "küçük": "Minimal yaşam tarzı için ideal, ısıtma maliyeti düşük",
        "otopark yok": "Alternatif ulaşım seçeneklerine yakın konum",
    }
    bulunan_problem = "Doğrudan listeleme yapılacak — belirgin bir dezavantaj tespit edilmedi."
    for anahtar, aciklama in problem_ipuclari.items():
        if anahtar in metin:
            bulunan_problem = aciklama
            break

    # İHTİYAÇ / HEDEF KİTLE tespiti
    if any(k in metin for k in ["öğrenci", "stüdyo", "1+0", "1+1"]):
        hedef = "Öğrenci / Genç Profesyonel"
        dil = "dinamik, bağımsızlık vurgulu, kira getirisi odaklı"
    elif any(k in metin for k in ["3+1", "4+1", "5+1", "geniş", "aile", "okul"]):
        hedef = "Aile"
        dil = "güvenli, sıcak, uzun vadeli düşünen, okul/ulaşım bilgisi öncelikli"
    elif any(k in metin for k in ["yatırım", "kira", "arsa", "ticari", "dükkan"]):
        hedef = "Yatırımcı"
        dil = "ROI odaklı, kira getirisi, değer artışı, teknik ve net"
    elif any(k in metin for k in ["ofis", "işyeri", "şirket"]):
        hedef = "İş İnsanı / Kurumsal"
        dil = "profesyonel, verimlilik odaklı, prestij vurgulu"
    else:
        hedef = "Geniş Kitle"
        dil = "dengeli, hem duygusal hem teknik, kapsamlı"

    # RİSK / GÜVEN tespiti (Kayseri'ye özel dinamikler)
    risk_notlar = []
    if "takas" in metin:
        risk_notlar.append("✅ Takas seçeneği mevcut — esneklik avantajı açıkça belirtilecek")
    if any(k in metin for k in ["kredi", "mortgage", "banka"]):
        risk_notlar.append("✅ Kredi kullanımına uygunluk vurgulanacak")
    if any(k in metin for k in ["pazarlık", "görüşülür", "konuşulur"]):
        risk_notlar.append("✅ Fiyat esnekliği müzakere davetiyesi olarak sunulacak")
    if any(k in metin for k in ["net", "fiyatı net", "sabit"]):
        risk_notlar.append("⚠️ Net fiyat — güven unsuru olarak öne çıkarılacak")
    if not risk_notlar:
        risk_notlar.append("ℹ️ Standart satış koşulları — güven vurgulu dil kullanılacak")

    return {
        "problem_firsat": bulunan_problem,
        "hedef_kitle": hedef,
        "dil_tonu": dil,
        "risk_guven": risk_notlar,
    }


def dinamik_sistem_promptu_olustur(pdr: dict, profil: dict | None) -> str:
    """Emlakçı profili + PDR analizine göre kişiselleştirilmiş sistem promptu."""

    stil_aciklamasi = ""
    kelime_listesi = ""

    if profil:
        stil_map = {
            "esnaf":     "samimi, kısa cümleler kullanan, esnaf dili ile sıcak ama net",
            "kurumsal":  "kurumsal, detaylı, teknik bilgi ağırlıklı, prestij vurgulu",
            "dengeli":   "hem sıcak hem profesyonel, dengeli uzunlukta",
        }
        stil_aciklamasi = f"""
## Emlakçı Yazım Stili (Öğrenilmiş Tercihler)
- Yazım Tonu: {stil_map.get(profil['stil'], 'dengeli')}
- Tercih Edilen Kelimeler: {', '.join(profil['kelimeler'][:8]) if profil['kelimeler'] else 'genel Türkçe'}
- Ortalama Metin Uzunluğu: ~{profil['uzunluk']} karakter — bu uzunluğa sadık kal
"""
    return f"""Sen Kayseri'de uzman bir emlak danışmanı ve pazarlama metni yazarısın.
PDR (Problem-İhtiyaç-Risk) çerçevesini kullanarak, aşağıdaki analiz ışığında 3 farklı format üret.

## PDR Analizi
- **Problem/Fırsat:** {pdr['problem_firsat']}
- **Hedef Kitle:** {pdr['hedef_kitle']} — Dil tonu: {pdr['dil_tonu']}
- **Risk/Güven Notları:** {'; '.join(pdr['risk_guven'])}
{stil_aciklamasi}

## Çıktı Kuralları (KESİNLİKLE UYULACAK)
Yanıtını aşağıdaki JSON formatında ver, başka hiçbir metin ekleme:

{{
  "portal": "...",
  "whatsapp": "...",
  "instagram": "..."
}}

### Portal İlanı (sahibinden/emlakjet tarzı)
- SEO uyumlu başlık + gövde
- 150-300 kelime, paragraflar halinde
- Teknik detaylar (m², oda, kat, ısıtma) doğal dilde
- Güven unsurları ve iletişim CTA'sı
- Duygusal bağ kuran kapanış

### WhatsApp Durumu
- Max 3-4 satır
- Emojiler kullan 🏠✅💰
- FOMO / aciliyet hissi ("Son 1 fırsat", "Bu hafta sonu kaçmaz")
- Direkt telefon CTA'sı
- Kısa, enerjik, harekete geçirici

### Instagram Post
- Görüntüyü tamamlayan açıklama (150-200 karakter)
- Yaşam tarzı sunumu
- 10-15 alakalı hashtag (Türkçe + İngilizce karışık)
- Emoji destekli, modern dil
"""


def claude_http_ile_cagir(sistem_promptu: str, kullanici_mesaji: str, api_key: str) -> str:
    """Anthropic Claude API — saf urllib, ekstra kütüphane gerektirmez."""
    import urllib.request as _ur
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1200,
        "system": sistem_promptu,
        "messages": [{"role": "user", "content": kullanici_mesaji}],
    }).encode("utf-8")
    req = _ur.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with _ur.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    raw = data["content"][0]["text"]
    return re.sub(r"```json\s*|\s*```", "", raw).strip()


def llm_ile_uret(ham_veri: str, pdr: dict, profil: dict | None,
                  api_tipi: str, api_key: str) -> dict:
    """LLM API'ye istek gönder, JSON yanıtı döndür."""
    sistem_promptu = dinamik_sistem_promptu_olustur(pdr, profil)
    kullanici_mesaji = f"Ham Emlak Verisi:\n{ham_veri}"

    if api_tipi == "claude" and api_key:
        raw = claude_http_ile_cagir(sistem_promptu, kullanici_mesaji, api_key)

    elif api_tipi == "openai" and OPENAI_AVAILABLE and api_key:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sistem_promptu},
                {"role": "user", "content": kullanici_mesaji}
            ],
            temperature=0.75,
            max_tokens=1200,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content

    elif api_tipi == "gemini" and GEMINI_AVAILABLE and api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={"temperature": 0.75, "max_output_tokens": 1200},
            system_instruction=sistem_promptu,
        )
        response = model.generate_content(kullanici_mesaji)
        raw = re.sub(r"```json\s*|\s*```", "", response.text).strip()

    else:
        raise ValueError("Geçerli bir API türü ve anahtarı sağlanmalı.")

    return json.loads(raw)

def demo_metin_uret(ham_veri: str, pdr: dict) -> dict:
    """API yokken gerçekçi demo metinler üret."""
    hedef = pdr['hedef_kitle']
    takas = "takas" in ham_veri.lower()
    takas_notu = " Takas seçeneğimiz mevcut." if takas else ""

    portal = f"""🏠 Kayseri'de Yatırım Değeri Yüksek, Huzurlu Yaşam Alanı

Kayseri'nin gözde semtlerinden birinde yer alan bu mülk, {hedef.lower()} için ideal koşulları bir arada sunuyor.

✅ Güneş alan cephesiyle sabahları doğal ışık doluyor. Bakımlı binanın konumu, şehrin tüm olanaklarına yürüme mesafesinde.

🔑 Öne Çıkan Özellikler:
• Yeni boya ve kısmi yenileme
• Kombi ısıtma sistemi
• Asansörlü bina
• Otopark imkânı

💬 Fiyatımız Kayseri piyasasının gerçeğine göre belirlenmiştir. Randevu almak ve detaylı bilgi edinmek için bizi arayın.{takas_notu}

📞 Bizi Arayın — Fırsatı Kaçırmayın!"""

    whatsapp = f"""🏠 Kayseri'de {hedef} İçin Mükemmel Fırsat!
✅ Temiz, bakımlı, hemen taşınılabilir
💰 Piyasanın altında fiyat — bu hafta sonu kapanıyor!
{('🔄 Takas görüşülür!' if takas else '📞 Arayın, müzakere edelim!')}
👉 Detay için mesaj atın ⬇️"""

    instagram = f"""🏡 Hayalinizdeki ev Kayseri'de sizi bekliyor!
✨ Modern yaşam, merkezi konum, uygun fiyat.
{('🔄 Takas seçeneğimiz var!' if takas else '💬 Randevu için DM!')}
.
.
#kayseri #kayseriemla̋k #satılıkdaire #kayseriyaşam #emlak #evinizibuluyoruz #taşınmak #yatırım #konut #gayrimenkul #kayserisatılık #evdekorasyon #kayserilife #realestateturkey #homesforsale"""

    return {"portal": portal, "whatsapp": whatsapp, "instagram": instagram}


# ─────────────────────────────────────────────
# UI YARDIMCI FONKSİYONLARI
# ─────────────────────────────────────────────

def kopya_butonu(metin: str, anahtar: str, etiket: str = "📋 Kopyala"):
    """Panoya kopyalama butonu (JS ile)."""
    escaped = metin.replace("`", "\\`").replace("$", "\\$")
    copy_js = f"""
    <button onclick="
      navigator.clipboard.writeText(`{escaped}`)
        .then(() => {{
          this.textContent = '✅ Kopyalandı!';
          this.style.background = 'linear-gradient(135deg,#065f46,#047857)';
          setTimeout(() => {{
            this.textContent = '{etiket}';
            this.style.background = '';
          }}, 2500);
        }})
        .catch(() => {{
          this.textContent = '❌ Manuel kopyalayın';
          setTimeout(() => {{ this.textContent = '{etiket}'; }}, 2500);
        }});
    " style="
      width:100%; padding:12px 16px; border-radius:10px;
      background:linear-gradient(135deg,#1e3a5f,#1e40af);
      color:white; font-weight:700; font-size:14px;
      border:1px solid rgba(99,179,237,0.3);
      cursor:pointer; margin-top:10px; transition:all 0.2s;
    ">{etiket}</button>
    """
    st.components.v1.html(copy_js, height=56)


def pdr_rozet_goster(pdr: dict):
    html = f"""
    <div style="margin:12px 0 6px">
      <span class="pdr-badge badge-p">🔴 P: {pdr['problem_firsat'][:45]}…</span>
      <span class="pdr-badge badge-d">🟢 D: {pdr['hedef_kitle']}</span>
      {''.join(f'<span class="pdr-badge badge-r">🟡 {r}</span>' for r in pdr['risk_guven'][:2])}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE BAŞLATMA
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "uretildi": False,
        "portal": "", "whatsapp": "", "instagram": "",
        "pdr": {}, "ilan_id": None,
        "ham_veri": "", "emlakci_id": "varsayilan",
        "duzeltme_portal": "", "duzeltme_wa": "", "duzeltme_ig": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────
# ANA UYGULAMA
# ─────────────────────────────────────────────
def main():
    init_db()
    init_state()

    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

    # ── HEADER ──
    st.markdown("""
    <div class="app-header">
        <h1>🏠 Akıllı İlan Fabrikası</h1>
        <p>Saniyeler içinde profesyonel emlak ilanları • PDR Analizi • AI Destekli</p>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR: AYARLAR ──
    with st.sidebar:
        st.markdown("### ⚙️ API Ayarları")

        api_tipi = st.selectbox(
            "LLM Sağlayıcı",
            ["demo (API yok)", "claude", "gemini", "openai"],
            help="Demo modda gerçekçi örnek metin üretilir."
        )

        api_key = ""
        if api_tipi != "demo (API yok)":
            env_key = os.getenv("ANTHROPIC_API_KEY" if api_tipi == "claude" else ("OPENAI_API_KEY" if api_tipi == "openai" else "GEMINI_API_KEY"), "")
            api_key = st.text_input(
                "API Anahtarı",
                value=env_key,
                type="password",
                placeholder=".env'den otomatik alındı",
            )

        st.divider()
        st.markdown("### 👤 Emlakçı Profili")
        emlakci_id = st.text_input("Emlakçı ID / Adı", value=st.session_state.emlakci_id)
        if emlakci_id:
            st.session_state.emlakci_id = emlakci_id

        profil = profil_getir(emlakci_id)
        if profil:
            st.markdown(f"""
            <div class="profile-score">
              <strong style="color:#34d399">📊 Öğrenilmiş Profiliniz</strong><br>
              <small>Stil: <b>{profil['stil'].upper()}</b> &nbsp;|&nbsp; Toplam İlan: <b>{profil['toplam_ilan']}</b></small><br>
              <small>Tercih: {', '.join(profil['kelimeler'][:5]) or '(henüz yok)'}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🆕 Yeni profil — ilk ilanınızı üretin!")

        st.divider()
        st.markdown("### 📋 Son İlanlarım")
        sonlar = son_ilanlar_getir(emlakci_id, 4)
        if sonlar:
            for s in sonlar:
                tarih = s[1][:10] if s[1] else ""
                kisa = (s[2] or "")[:35]
                st.caption(f"📅 {tarih} — {kisa}…")
        else:
            st.caption("Henüz ilan oluşturulmadı.")

    # ═══════════════════════════════════════════
    # GİRDİ ALANI
    # ═══════════════════════════════════════════
    st.markdown('<div class="card-title">✍️ Ham Emlak Verisini Gir</div>', unsafe_allow_html=True)

    with st.expander("💡 Nasıl yazmalıyım? (Örnekler)", expanded=False):
        st.markdown("""
**Hızlı format:** `3+1, Talas Akasya, 4.Kat, 120m², kombi, 4 Milyon TL, takas olur, boyası yeni`

**Daha detaylı:**
> Kocasinan merkez, 2+1, 3. kat, 85m², asansörsüz, 2.8m tavan yüksekliği, doğalgaz,
> 2.750.000 TL net fiyat, kredi uygun, balkon var, mahalle market yanı.

**Sesli not transkripti de yapıştırabilirsiniz ✅**
        """)

    ham_veri = st.text_area(
        label="Ham Veri",
        placeholder="Örn: 3+1, Talas, 4 Milyon, takas olur, boyası yeni, kombili, 120m²...",
        height=130,
        label_visibility="collapsed",
        key="ham_veri_input",
    )

    # ── SESLİ GİRİŞ (Web Speech API — kurulum gerektirmez, Chrome'da çalışır) ──
    with st.expander("🎤 Sesli Giriş — Mikrofona Konuş", expanded=False):
        st.caption("🟢 Chrome / Edge tarayıcısında çalışır. Butona bas, Türkçe konuş, metni kopyala.")

        ses_html = """
<div style="font-family:Inter,sans-serif; padding:12px; background:#0f172a;
     border-radius:14px; border:1px solid rgba(99,179,237,0.2);">

  <div id="status" style="color:#94a3b8; font-size:13px; margin-bottom:12px; text-align:center;">
    🎤 Hazır — butona bas ve konuş
  </div>

  <textarea id="sesMetin" rows="4" placeholder="Konuşunca burada görünür..."
    style="width:100%; background:#1e293b; color:#e2e8f0; border:1px solid rgba(99,179,237,0.2);
           border-radius:10px; padding:12px; font-size:14px; resize:none; box-sizing:border-box;
           margin-bottom:10px;"></textarea>

  <div style="display:flex; gap:8px;">
    <button id="baslatBtn" onclick="baslatDinleme()" style="
      flex:1; padding:14px; background:linear-gradient(135deg,#dc2626,#b91c1c);
      color:white; border:none; border-radius:10px; font-size:15px;
      font-weight:700; cursor:pointer;">
      🔴 Konuşmaya Başla
    </button>
    <button onclick="temizle()" style="
      padding:14px 18px; background:#1e293b; color:#94a3b8;
      border:1px solid rgba(99,179,237,0.2); border-radius:10px;
      font-size:13px; cursor:pointer;">
      🗑️
    </button>
  </div>

  <button onclick="kopyala()" style="
    width:100%; margin-top:8px; padding:12px;
    background:linear-gradient(135deg,#065f46,#047857);
    color:white; border:none; border-radius:10px;
    font-size:14px; font-weight:700; cursor:pointer;">
    📋 Metni Kopyala → Ham Veri Alanına Yapıştır
  </button>

  <div id="kopyaMesaj" style="display:none; color:#34d399; text-align:center;
       font-size:13px; margin-top:8px;">✅ Kopyalandı! Ham veri alanına yapıştır (Ctrl+V)</div>
</div>

<script>
let recognition = null;
let dinliyor = false;

function baslatDinleme() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    document.getElementById('status').innerHTML =
      '❌ Tarayıcınız desteklemiyor. Chrome veya Edge kullanın.';
    document.getElementById('status').style.color = '#f87171';
    return;
  }

  if (dinliyor) {
    recognition.stop();
    return;
  }

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = 'tr-TR';
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onstart = () => {
    dinliyor = true;
    document.getElementById('baslatBtn').textContent = '⏹ Durdur';
    document.getElementById('baslatBtn').style.background = 'linear-gradient(135deg,#1d4ed8,#1e40af)';
    document.getElementById('status').innerHTML = '🔴 Dinleniyor... Konuşun';
    document.getElementById('status').style.color = '#34d399';
  };

  recognition.onresult = (e) => {
    let metin = '';
    for (let i = 0; i < e.results.length; i++) {
      metin += e.results[i][0].transcript;
    }
    document.getElementById('sesMetin').value = metin;
  };

  recognition.onend = () => {
    dinliyor = false;
    document.getElementById('baslatBtn').textContent = '🔴 Konuşmaya Başla';
    document.getElementById('baslatBtn').style.background = 'linear-gradient(135deg,#dc2626,#b91c1c)';
    document.getElementById('status').innerHTML = '✅ Tamamlandı — metni kopyalayın';
    document.getElementById('status').style.color = '#63b3ed';
  };

  recognition.onerror = (e) => {
    document.getElementById('status').innerHTML = '❌ Hata: ' + e.error + ' — tekrar deneyin';
    document.getElementById('status').style.color = '#f87171';
    dinliyor = false;
  };

  recognition.start();
}

function temizle() {
  document.getElementById('sesMetin').value = '';
  document.getElementById('status').innerHTML = '🎤 Hazır — butona bas ve konuş';
  document.getElementById('status').style.color = '#94a3b8';
}

function kopyala() {
  const metin = document.getElementById('sesMetin').value;
  if (!metin) return;
  navigator.clipboard.writeText(metin).then(() => {
    document.getElementById('kopyaMesaj').style.display = 'block';
    setTimeout(() => {
      document.getElementById('kopyaMesaj').style.display = 'none';
    }, 3000);
  });
}
</script>
"""
        st.components.v1.html(ses_html, height=320)
        st.info("💡 Konuştuktan sonra 'Metni Kopyala' → yukarıdaki Ham Veri kutusuna yapıştır (Ctrl+V / uzun bas)")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ÜRET BUTONU ──
    uret_col, _ = st.columns([3, 1])
    with uret_col:
        buton_basıldı = st.button(
            "⚡ İlan Metinlerini Üret",
            type="primary",
            use_container_width=True,
            disabled=len(ham_veri.strip()) < 10,
        )

    if len(ham_veri.strip()) < 10 and not st.session_state.uretildi:
        st.caption("⬆️ En az 10 karakter veri girin.")

    # ═══════════════════════════════════════════
    # ÜRETİM LOJİĞİ
    # ═══════════════════════════════════════════
    if buton_basıldı and len(ham_veri.strip()) >= 10:
        st.session_state.ham_veri = ham_veri
        pdr = pdr_analizi_yap(ham_veri)
        st.session_state.pdr = pdr
        profil = profil_getir(st.session_state.emlakci_id)

        with st.spinner("🤖 PDR analizi yapılıyor ve metinler üretiliyor..."):
            try:
                if api_tipi != "demo (API yok)" and api_key:
                    sonuclar = llm_ile_uret(ham_veri, pdr, profil, api_tipi, api_key)
                else:
                    sonuclar = demo_metin_uret(ham_veri, pdr)

                st.session_state.portal    = sonuclar.get("portal", "")
                st.session_state.whatsapp  = sonuclar.get("whatsapp", "")
                st.session_state.instagram = sonuclar.get("instagram", "")

                # Düzeltme alanlarını sıfırla
                st.session_state.duzeltme_portal = st.session_state.portal
                st.session_state.duzeltme_wa     = st.session_state.whatsapp
                st.session_state.duzeltme_ig     = st.session_state.instagram

                # DB'ye kaydet
                ilan_id = kaydet_ilan(
                    ham_veri, pdr,
                    st.session_state.portal, st.session_state.whatsapp, st.session_state.instagram,
                    pdr['hedef_kitle'], st.session_state.emlakci_id
                )
                st.session_state.ilan_id = ilan_id
                st.session_state.uretildi = True

            except json.JSONDecodeError:
                st.error("⚠️ LLM yanıtı JSON formatında değildi. Tekrar deneyin.")
            except Exception as e:
                st.error(f"⚠️ Hata: {str(e)}")
                if api_tipi != "demo (API yok)":
                    st.info("Demo moduna geçiliyor...")
                    sonuclar = demo_metin_uret(ham_veri, pdr)
                    st.session_state.portal    = sonuclar.get("portal", "")
                    st.session_state.whatsapp  = sonuclar.get("whatsapp", "")
                    st.session_state.instagram = sonuclar.get("instagram", "")
                    st.session_state.duzeltme_portal = st.session_state.portal
                    st.session_state.duzeltme_wa     = st.session_state.whatsapp
                    st.session_state.duzeltme_ig     = st.session_state.instagram
                    ilan_id = kaydet_ilan(
                        ham_veri, pdr,
                        st.session_state.portal, st.session_state.whatsapp, st.session_state.instagram,
                        pdr['hedef_kitle'], st.session_state.emlakci_id
                    )
                    st.session_state.ilan_id = ilan_id
                    st.session_state.uretildi = True

    # ═══════════════════════════════════════════
    # ÇIKTI ALANI
    # ═══════════════════════════════════════════
    if st.session_state.uretildi and st.session_state.portal:

        st.divider()
        st.markdown("### 📊 PDR Analiz Sonucu")
        pdr_rozet_goster(st.session_state.pdr)

        st.divider()
        st.markdown("### 📝 Üretilen İlan Metinleri")

        tab1, tab2, tab3 = st.tabs(["🏢 Portal İlanı", "💬 WhatsApp", "📸 Instagram"])

        # ── TAB 1: PORTAL ──
        with tab1:
            st.markdown(f"""
            <div class="card-title">🏢 Portal İlanı (Sahibinden / Emlakjet)</div>
            <div class="output-box">{st.session_state.portal}</div>
            """, unsafe_allow_html=True)
            kopya_butonu(st.session_state.portal, "portal", "📋 Portal Metnini Kopyala")

            with st.expander("✏️ Metni Düzelt ve Kaydet"):
                duz_portal = st.text_area(
                    "Düzenle:", value=st.session_state.duzeltme_portal,
                    height=200, key="duz_portal_input", label_visibility="collapsed"
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👍 Beğen & Kaydet", key="begen_portal", use_container_width=True):
                        kaydet_geri_bildirim(
                            st.session_state.ilan_id, "portal",
                            st.session_state.portal, duz_portal, 1,
                            st.session_state.emlakci_id
                        )
                        st.success("✅ Geri bildirim kaydedildi! Profiliniz güncellendi.")
                with c2:
                    if st.button("💾 Düzeltmeyi Kaydet", key="duz_kaydet_portal", use_container_width=True):
                        kaydet_geri_bildirim(
                            st.session_state.ilan_id, "portal",
                            st.session_state.portal, duz_portal, 0,
                            st.session_state.emlakci_id
                        )
                        st.session_state.duzeltme_portal = duz_portal
                        st.success("💾 Düzeltme kaydedildi.")

        # ── TAB 2: WHATSAPP ──
        with tab2:
            st.markdown(f"""
            <div class="card-title">💬 WhatsApp Durumu</div>
            <div class="output-box">{st.session_state.whatsapp}</div>
            """, unsafe_allow_html=True)
            kopya_butonu(st.session_state.whatsapp, "whatsapp", "📋 WhatsApp Metnini Kopyala")

            with st.expander("✏️ Metni Düzelt ve Kaydet"):
                duz_wa = st.text_area(
                    "Düzenle:", value=st.session_state.duzeltme_wa,
                    height=140, key="duz_wa_input", label_visibility="collapsed"
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👍 Beğen & Kaydet", key="begen_wa", use_container_width=True):
                        kaydet_geri_bildirim(
                            st.session_state.ilan_id, "whatsapp",
                            st.session_state.whatsapp, duz_wa, 1,
                            st.session_state.emlakci_id
                        )
                        st.success("✅ Geri bildirim kaydedildi!")
                with c2:
                    if st.button("💾 Düzeltmeyi Kaydet", key="duz_kaydet_wa", use_container_width=True):
                        kaydet_geri_bildirim(
                            st.session_state.ilan_id, "whatsapp",
                            st.session_state.whatsapp, duz_wa, 0,
                            st.session_state.emlakci_id
                        )
                        st.success("💾 Düzeltme kaydedildi.")

        # ── TAB 3: INSTAGRAM ──
        with tab3:
            st.markdown(f"""
            <div class="card-title">📸 Instagram Post / Reels</div>
            <div class="output-box">{st.session_state.instagram}</div>
            """, unsafe_allow_html=True)
            kopya_butonu(st.session_state.instagram, "instagram", "📋 Instagram Metnini Kopyala")

            with st.expander("✏️ Metni Düzelt ve Kaydet"):
                duz_ig = st.text_area(
                    "Düzenle:", value=st.session_state.duzeltme_ig,
                    height=160, key="duz_ig_input", label_visibility="collapsed"
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👍 Beğen & Kaydet", key="begen_ig", use_container_width=True):
                        kaydet_geri_bildirim(
                            st.session_state.ilan_id, "instagram",
                            st.session_state.instagram, duz_ig, 1,
                            st.session_state.emlakci_id
                        )
                        st.success("✅ Geri bildirim kaydedildi!")
                with c2:
                    if st.button("💾 Düzeltmeyi Kaydet", key="duz_kaydet_ig", use_container_width=True):
                        kaydet_geri_bildirim(
                            st.session_state.ilan_id, "instagram",
                            st.session_state.instagram, duz_ig, 0,
                            st.session_state.emlakci_id
                        )
                        st.success("💾 Düzeltme kaydedildi.")

        st.divider()

        # ── YENİ İLAN BUTONU ──
        if st.button("🔄 Yeni İlan Üret", use_container_width=True):
            for k in ["uretildi", "portal", "whatsapp", "instagram", "pdr", "ilan_id",
                       "ham_veri", "duzeltme_portal", "duzeltme_wa", "duzeltme_ig"]:
                st.session_state[k] = "" if isinstance(st.session_state.get(k), str) else (
                    False if k == "uretildi" else (None if k == "ilan_id" else {})
                )
            st.rerun()

    # ── ALT BİLGİ ──
    st.markdown("""
    <div style="text-align:center; color:#475569; font-size:11px; margin-top:24px; padding-bottom:16px;">
        Akıllı İlan Fabrikası • PDR Analizi + SQLite Öğrenim • Kayseri Odaklı
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
