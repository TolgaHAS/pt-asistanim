import streamlit as st
import google.generativeai as genai

# --- 1. SAYFA AYARLARI (En başta olmalı) ---
st.set_page_config(
    page_title="HAS Team PT",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. TASARIM: GÖRSELDEKİ "MIDNIGHT TEAL" TEMASI (GÜNCELLENMİŞ) ---
st.markdown("""
    <style>
    /* APP ARKA PLANI (Çok koyu lacivert/siyah) */
    .stApp {
        background-color: #05070A; 
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }

    /* FORM KART TASARIMI (Görseldeki Kutu) */
    [data-testid="stForm"] {
        background-color: #0E121B; /* Kart Rengi */
        border: 1px solid #1E2330;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }

    /* INPUT ALANLARI (İsim, Yaş, Kilo vb.) */
    .stTextInput label {
        color: #A0AEC0 !important; /* Label rengi */
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 5px; /* Label ile input arası boşluk */
        display: block; /* Label'ı blok element yap */
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div, .stTextArea textarea {
        background-color: #161B29 !important; /* Input Zemin */
        color: #E0E0E0 !important;
        border: 1px solid #2A3245 !important;
        border-radius: 8px !important;
        height: 45px; /* Biraz daha yüksek */
        padding: 10px 15px; /* İç boşluk */
    }
    
    /* Input Focus Durumu */
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: #00D285 !important; /* HAS Yeşil */
        box-shadow: 0 0 0 1px #00D285;
    }
    
    /* Number Input'taki artırma/azaltma butonları */
    .stNumberInput button {
        background-color: #161B29 !important; /* Buton arka planı */
        border: 1px solid #2A3245 !important;
        color: #E0E0E0 !important;
        border-radius: 8px;
    }
    .stNumberInput button:hover {
        background-color: #00D285 !important; /* Hover rengi */
        color: #0E121B !important;
    }


    /* Selectbox Ok Simgesi */
    .stSelectbox div[data-baseweb="select"] span {
        color: #E0E0E0 !important;
    }

    /* BAŞLIKLAR (Genel Uygulama Başlığı ve Form İçi Başlıklar) */
    h1 {
        color: #00D285 !important; /* Ana Başlık Yeşili */
        font-weight: 700;
        text-align: center;
        font-size: 2.5rem !important; /* Daha büyük */
        margin-bottom: 0.5rem;
    }
    
    /* Form içindeki alt başlıklar (Örn: Temel Bilgiler) */
    h4 {
        color: #FFFFFF !important; /* Beyaz */
        font-size: 1.25rem !important; /* Daha okunaklı */
        font-weight: 600;
        margin-bottom: 20px !important;
        display: flex;
        align-items: center;
        gap: 10px; /* İkon ile yazı arası boşluk */
    }
    
    /* Formdaki Temel Bilgiler başlığındaki ikon */
    h4 .icon {
        color: #00D285; /* İkon rengi */
    }


    /* SUBTITLE (Alt Başlık) */
    .subtitle {
        color: #718096;
        text-align: center;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    /* "DEVAM ET" BUTONU (Görseldeki Yeşil Geniş Buton) */
    .stButton > button {
        background-color: #00A86B !important; /* Koyu Yeşil */
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        padding: 0.75rem 1rem;
        width: 100%; /* Tam genişlik */
        transition: all 0.2s;
        display: flex; /* İkonu ortalamak için */
        justify-content: center;
        align-items: center;
        gap: 8px; /* Buton metni ile ikon arası boşluk */
    }
    .stButton > button:hover {
        background-color: #00C07A !important; /* Hover Açık Yeşil */
        transform: translateY(-1px);
    }
    
    /* Slider Rengi */
    div[data-baseweb="slider"] div {
        background-color: #00D285 !important;
    }
    
    /* Sekmeler (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 15px; /* Sekmeler arası boşluk */
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent; /* Sekme arka planı şeffaf */
        color: #718096;
        border: none;
        padding: 10px 15px;
        font-weight: 500;
        transition: color 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #E0E0E0;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #00D285 !important;
        font-weight: 600;
        border-bottom: 2px solid #00D285 !important; /* Aktif sekme alt çizgisi */
    }

    /* Chat Baloncukları */
    .stChatMessage {
        background-color: #0E121B;
        border: 1px solid #1E2330;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .stChatMessage p {
        color: #E0E0E0; /* Chat mesajı metin rengi */
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #4A5568;
        font-size: 12px;
        margin-top: 30px; /* Alttan boşluk */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. OTURUM YÖNETİMİ (SESSION STATE) ---
if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. API ANAHTARI KONTROLÜ ---
try:
    api_key = st.secrets["google_apikey"]
except:
    api_key = None

# ==================================================
# MOD 1: ONBOARDING (GÖRSELDEKİ FORM EKRANI)
# ==================================================
if not st.session_state.profile_complete:
    
    # Sayfayı ortalamak için boşluk
    st.write("") 
    
    # Kartı ortalamak için kolon yapısı (Mobil/Desktop uyumlu)
    col_l, col_main, col_r = st.columns([1, 1.5, 1])

    with col_main:
        # --- BAŞLIK ALANI (Custom HTML) ---
        st.markdown("<h1>HAS Team PT</h1>", unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Kişisel Antrenörünüz sizi tanımak istiyor.</p>', unsafe_allow_html=True)
        
        # Görseldeki Pagination Dots (Aktif/Pasif durumları da düzenledim)
        st.markdown("""
            <div style="display: flex; justify-content: center; gap: 5px; margin-bottom: 30px;">
                <div style="width: 20px; height: 4px; background-color: #00D285; border-radius: 2px;"></div>
                <div style="width: 6px; height: 4px; background-color: #2D3748; border-radius: 2px;"></div>
                <div style="width: 6px; height: 4px; background-color: #2D3748; border-radius: 2px;"></div>
            </div>
        """, unsafe_allow_html=True)

        # --- FORM BAŞLANGICI ---
        with st.form("onboarding_form"):
            
            # Form içindeki "Temel Bilgiler" başlığı (İkon eklendi)
            st.markdown('<h4 style="color:white; margin-bottom:20px;"><span class="icon">📝</span> Temel Bilgiler</h4>', unsafe_allow_html=True)
            
            # İsim
            st.text_input("İsim", key="name_input", placeholder="Adınız")
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # Boşluk ekleme

            # Yaş ve Cinsiyet
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Yaş", min_value=10, max_value=90, value=25)
            with c2:
                gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın", "Belirtmek İstemiyorum"])
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # Boşluk ekleme

            # Boy ve Kilo
            c3, c4 = st.columns(2)
            with c3:
                height = st.number_input("Boy (cm)", min_value=100, max_value=250, value=175)
            with c4:
                weight = st.number_input("Kilo (kg)", min_value=30, max_value=200, value=75)
            st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True) # Bölüm arası boşluk

            st.markdown('<h4 style="color:white; margin-bottom:20px;"><span class="icon">🎯</span> Hedef ve Durum</h4>', unsafe_allow_html=True)

            # Hedef
            goal = st.text_input("Ana Hedefiniz Nedir?", placeholder="Örn: Yağ oranımı %12'ye düşürmek istiyorum")
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # Boşluk ekleme
            
            # Kondisyon
            fitness_level = st.select_slider(
                "Mevcut Kondisyon Seviyesi", 
                options=["Başlangıç", "Düşük", "Orta", "İleri", "Atletik"]
            )
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # Boşluk ekleme
            
            # Aktivite & Geçmiş
            activity_level = st.selectbox("Günlük Aktivite", ["Masa başı", "Az hareketli", "Hareketli", "Çok hareketli"])
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # Boşluk ekleme
            sports_history = st.text_input("Spor Geçmişi", placeholder="Örn: 2 yıl önce fitness yaptım.")
            st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True) # Bölüm arası boşluk

            st.markdown('<h4 style="color:white; margin-bottom:20px;"><span class="icon">⚙️</span> Detaylar</h4>', unsafe_allow_html=True)
            
            injuries = st.text_input("Sakatlık Durumu", placeholder="Varsa belirtin...")
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # Boşluk ekleme
            equipment = st.multiselect("Ekipman Erişimi", ["Spor Salonu", "Dumbbell", "Barbell", "Direnç Bandı", "Vücut Ağırlığı"])
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # Boşluk ekleme
            lifestyle_details = st.text_area("Uyku ve Zaman", placeholder="Günde kaç saat uyuyorsunuz? Ne kadar vaktiniz var?", height=80)

            st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True) # Buton öncesi boşluk
            
            # BUTON
            submit_btn = st.form_submit_button("Devam Et ➔")

            if submit_btn:
                # İsim input'unu session state'den alıyoruz çünkü form içinde key verdik
                name_val = st.session_state.name_input
                
                if name_val and goal:
                    st.session_state.user_data = {
                        "name": name_val,
                        "gender": gender,
                        "age": age,
                        "height": height,
                        "weight": weight,
                        "goal": goal,
                        "fitness_level": fitness_level,
                        "activity": activity_level,
                        "history": sports_history,
                        "injuries": injuries,
                        "equipment": equipment,
                        "lifestyle": lifestyle_details
                    }
                    st.session_state.profile_complete = True
                    st.rerun()
                else:
                    st.error("Lütfen isim ve hedef alanlarını doldurunuz.")
        
        st.markdown('<div class="footer">Powered by Gemini 2.5 Flash & HAS Team Methodology</div>', unsafe_allow_html=True)

# ==================================================
# MOD 2: ANA UYGULAMA (LOGIC AYNI KALIYOR)
# ==================================================
else:
    user = st.session_state.user_data
    
    # --- AI MODEL AYARLARI ---
    system_instruction = f"""
    Sen bir HAS Team Kişisel Antrenörüsün.
    KULLANICI: {user.get('name')}, {user.get('age')} yaşında, {user.get('weight')}kg.
    HEDEF: {user.get('goal')}.
    SAKATLIK: {user.get('injuries')}.
    EKİPMAN: {user.get('equipment')}.
    
    Görevin: Bilimsel, motive edici ve sürdürülebilir programlar hazırlamak.
    Format: Markdown tabloları kullan.
    """

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction)
        
        # Header
        c_head1, c_head2 = st.columns([1, 8])
        with c_head2:
            st.markdown(f"<h1>HAS Team PT | {user.get('name')}</h1>", unsafe_allow_html=True)
            st.caption(f"Hedef: {user.get('goal')}")
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["💬 AI Koç", "🍎 Beslenme", "🏋️ Antrenman", "👤 Profil"])

        # --- SOHBET ---
        with tab1:
            if not st.session_state.messages:
                initial_msg = f"Selam {user.get('name')}! Profilini aldım. {user.get('goal')} hedefin için hazırım."
                st.session_state.messages.append({"role": "model", "content": initial_msg})
            
            for message in st.session_state.messages:
                role = "user" if message["role"] == "user" else "assistant"
                with st.chat_message(role):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Koçuna sor..."):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                try:
                    chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages])
                    response = chat.send_message(prompt)
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                except Exception as e:
                    st.error(f"Hata: {e}")

        # --- DİĞER TABLAR (Mantık Aynı) ---
        with tab2:
            st.info("Beslenme Planı")
            if st.button("Örnek Diyet Listesi"):
                res = model.generate_content("1 günlük örnek diyet listesi hazırla.")
                st.markdown(res.text)

        with tab3:
            st.info("Antrenman Programı")
            if st.button("Program Oluştur"):
                res = model.generate_content("Haftalık antrenman programı hazırla.")
                st.markdown(res.text)

        with tab4:
            st.json(user)
            if st.button("Çıkış Yap"):
                st.session_state.profile_complete = False
                st.session_state.messages = []
                st.rerun()
    
    else:
        st.error("API Key Eksik.")
