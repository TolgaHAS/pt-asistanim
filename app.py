import streamlit as st
import google.generativeai as genai

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="HAS Team PT",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. TASARIM: SİYAH & YEŞİL TEMA (CSS ENJEKSİYONU) ---
# Bu kısım arayüzü görseldeki gibi siyah/yeşil yapar.
st.markdown("""
    <style>
    /* GENEL ARKA PLAN */
    .stApp {
        background-color: #0E1117; /* Koyu Siyah/Lacivert */
        color: #FFFFFF;
    }

    /* BAŞLIKLAR (H1, H2, H3) - YEŞİL */
    h1, h2, h3 {
        color: #2bd48d !important; /* HAS Team Yeşili */
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    
    /* METİN RENGİ */
    p, div, label, .stMarkdown {
        color: #E0E0E0;
    }

    /* BUTONLAR - YEŞİL */
    .stButton > button {
        background-color: #2bd48d !important; /* Yeşil Buton */
        color: #000000 !important; /* Siyah Yazı */
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #22a86f !important; /* Hover Rengi */
        color: #fff !important;
        box-shadow: 0 0 10px rgba(43, 212, 141, 0.5);
    }

    /* INPUT ALANLARI (Chat Input vb.) */
    .stTextInput > div > div > input {
        background-color: #1C2026;
        color: white;
        border: 1px solid #2bd48d;
    }
    .stChatInput > div > div > textarea {
        background-color: #1C2026;
        color: white;
        border: 1px solid #444;
    }

    /* TABS (SEKMELER) TASARIMI */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1C2026;
        border-radius: 8px 8px 0 0;
        color: #aaa;
        border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2bd48d !important;
        color: #000 !important;
        font-weight: bold;
        border: none;
    }

    /* MESAJ KUTULARI */
    .stChatMessage {
        background-color: #13161c;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 3px solid #2bd48d;
    }
    
    /* INFO BOX */
    .stAlert {
        background-color: #1C2026;
        color: #fff;
        border: 1px solid #2bd48d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API KURULUMU ---
# Streamlit Cloud Secrets üzerinden API Key alınıyor
# Eğer lokalde çalışıyorsan buraya direkt string olarak yazabilirsin: api_key = "SENIN_KEYIN"
try:
    api_key = st.secrets["google_apikey"]
except:
    # Hata almamak için boş geçiyoruz, kullanıcıya uyarı vereceğiz
    api_key = None

# --- 4. BAŞLIK VE LOGO ALANI ---
col1, col2 = st.columns([1, 10])
with col1:
    st.write("💪") # Buraya logo resmi de eklenebilir: st.image("logo.png")
with col2:
    st.title("HAS Team - AI Coach")
st.markdown("---") # Yeşil çizgi etkisi için divider

# --- 5. SİSTEM PROMPT (Zeka) ---
system_instruction = """
Amaç:
Sen bir "HAS Team Kişisel Antrenörü"sün.
Görevin, kullanıcının fitness hedeflerini analiz etmek, kişisel özelliklerine göre kanıta dayalı, sürdürülebilir öneriler sunmaktır.
Motivasyonel, profesyonel ve "kanka" tonunda konuş.

ÖZELLİKLER:
1. Kısa ve net cevaplar ver.
2. Listeler ve tablolar kullan (okunabilirlik için).
3. Kullanıcıyı motive et ("Hadi şampiyon", "Bu set senin" gibi).
4. Beslenme ve antrenman konusunda bilimsel ama basit konuş.

Eğer kullanıcı bir program isterse önce şu detayları sor:
- Yaş, Boy, Kilo
- Hedef (Yağ yakımı / Kas kazanımı)
- Spor geçmişi ve Ekipman durumu.
"""

# --- 6. UYGULAMA MANTIĞI ---
if api_key:
    genai.configure(api_key=api_key)
    # Model tanımlama
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction)

    # Sekmeler
    tab1, tab2, tab3, tab4 = st.tabs(["💬 SOHBET & KOÇLUK", "🍎 BESLENME PLANI", "🏋️ ANTRENMAN", "📈 GELİŞİM TAKİBİ"])

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --- TAB 1: SOHBET ---
    with tab1:
        # Karşılama mesajı yoksa ekle
        if len(st.session_state.messages) == 0:
            st.info("👋 Selam Şampiyon! Ben HAS Team AI Koçun. Bugün hangi bölgeyi parçalıyoruz veya ne yiyoruz?")

        # Geçmiş mesajları göster
        for message in st.session_state.messages:
            role = "user" if message["role"] == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(message["content"])

        # Input alanı
        if prompt := st.chat_input("Buraya yazabilirsin..."):
            # Kullanıcı mesajını ekle
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # AI Cevabı
            try:
                chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages])
                response = chat.send_message(prompt)
                
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

    # --- TAB 2: BESLENME ---
    with tab2:
        col_b1, col_b2 = st.columns([2,1])
        with col_b1:
            st.header("🍎 Günlük Makro Planlayıcı")
            st.write("Senin için örnek bir beslenme düzeni oluşturabilirim.")
        with col_b2:
            # Görsellik için boşluk
            pass
            
        if st.button("Protein Ağırlıklı Örnek Menü Oluştur"):
            with st.spinner('Menü hazırlanıyor...'):
                req = "Bana sabah, öğle, akşam ve ara öğün içeren, protein ağırlıklı, tablo formatında bir günlük beslenme planı hazırla."
                response = model.generate_content(req)
                st.markdown(response.text)

    # --- TAB 3: ANTRENMAN ---
    with tab3:
        st.header("🏋️ Antrenman Oluşturucu")
        
        c1, c2 = st.columns(2)
        with c1:
            bolge = st.selectbox("Hedef Bölge", ["Tüm Vücut (Full Body)", "Göğüs & Triceps", "Sırt & Biceps", "Bacak & Kalça", "Omuz & Karın"])
        with c2:
            seviye = st.selectbox("Seviye", ["Başlangıç", "Orta", "İleri"])
            
        if st.button("Antrenmanı Hazırla 🚀"):
            with st.spinner('Antrenman programı yükleniyor...'):
                prompt_text = f"{seviye} seviyesinde, {bolge} odaklı, hipertrofi (kas büyümesi) amaçlı 5 hareketlik bir antrenman programı yaz. Tablo olarak ver. Set ve tekrar sayılarını belirt."
                response = model.generate_content(prompt_text)
                st.markdown(response.text)

    # --- TAB 4: TAKİP ---
    with tab4:
        st.header("📈 Haftalık Uyum Raporu")
        st.write("Haftalık ilerlemeni buraya not alacağız. (Yakında eklenecek)")
        st.progress(70, text="Haftalık Hedef Tamamlanma Oranı: %70")

else:
    st.warning("⚠️ API Key bulunamadı! Lütfen Streamlit Secrets ayarlarını kontrol et.")
    st.image("https://media.giphy.com/media/3o7aTskHEUdgCQAXde/giphy.gif", width=300)
