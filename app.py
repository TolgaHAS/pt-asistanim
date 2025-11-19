import streamlit as st
import google.generativeai as genai

# --- 1. SAYFA AYARLARI (En başta olmalı) ---
st.set_page_config(
    page_title="HAS Team PT",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. TASARIM: GÖRSELDEKİ "MIDNIGHT TEAL" TEMASI ---
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
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div, .stTextArea textarea {
        background-color: #161B29 !important; /* Input Zemin */
        color: #E0E0E0 !important;
        border: 1px solid #2A3245 !important;
        border-radius: 8px !important;
        height: 45px; /* Biraz daha yüksek */
    }
    
    /* Input Focus Durumu */
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: #00D285 !important; /* HAS Yeşil */
        box-shadow: 0 0 0 1px #00D285;
    }

    /* Label (Etiket) Renkleri */
    .stMarkdown label, p, .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #A0AEC0 !important;
        font-size: 14px;
        font-weight: 500;
    }

    /* BAŞLIKLAR */
    h1 {
        color: #00D285 !important; /* Başlık Yeşili */
        font-weight: 700;
        text-align: center;
        font-size: 2.2rem !important;
        margin-bottom: 0.5rem;
    }
    h2, h3 {
        color: #FFFFFF !important;
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
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0E121B;
        color: #718096;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #161B29 !important;
        color: #00D285 !important;
        border-bottom: 2px solid #00D285;
    }

    /* Chat Baloncukları */
    .stChatMessage {
        background-color: #0E121B;
        border: 1px solid #1E2330;
        border-radius: 12px;
    }
    
    /* Alt Bilgi */
    .footer {
        text-align: center;
        color: #4A5568;
        font-size: 12px;
        margin-top: 20px;
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
        
        # Görseldeki Pagination Dots (Süs olarak)
        st.markdown("""
            <div style="display: flex; justify-content: center; gap: 5px; margin-bottom: 20px;">
                <div style="width: 20px; height: 4px; background-color: #00D285; border-radius: 2px;"></div>
                <div style="width: 6px; height: 4px; background-color: #2D3748; border-radius: 2px;"></div>
                <div style="width: 6px; height: 4px; background-color: #2D3748; border-radius: 2px;"></div>
            </div>
        """, unsafe_allow_html=True)

        # --- FORM BAŞLANGICI ---
        with st.form("onboarding_form"):
            
            st.markdown('<h4 style="color:white; margin-bottom:10px;">🏷️ Temel Bilgiler</h4>', unsafe_allow_html=True)
            
            # İsim
            st.text_input("İsim", key="name_input", placeholder="Adınız")

            # Yaş ve Cinsiyet
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Yaş", min_value=10, max_value=90, value=25)
            with c2:
                gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın", "Belirtmek İstemiyorum"])

            # Boy ve Kilo
            c3, c4 = st.columns(2)
            with c3:
                height = st.number_input("Boy (cm)", min_value=100, max_value=250, value=175)
            with c4:
                weight = st.number_input("Kilo (kg)", min_value=30, max_value=200, value=75)

            st.markdown("---")
            st.markdown('<h4 style="color:white; margin-bottom:10px;">🎯 Hedef ve Durum</h4>', unsafe_allow_html=True)

            # Hedef
            goal = st.text_input("Ana Hedefiniz Nedir?", placeholder="Örn: Yağ oranımı %12'ye düşürmek istiyorum")
            
            #
