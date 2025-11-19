import streamlit as st
import google.generativeai as genai
from datetime import datetime

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
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label, .stMultiSelect label {
        color: #A0AEC0 !important; /* Label rengi */
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 5px; /* Label ile input arası boşluk */
        display: block; /* Label'ı blok element yap */
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div, .stTextArea textarea, .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #161B29 !important; /* Input Zemin */
        color: #E0E0E0 !important;
        border: 1px solid #2A3245 !important;
        border-radius: 8px !important;
        height: 45px; /* Biraz daha yüksek */
        padding: 10px 15px; /* İç boşluk */
    }
    
    /* Input Focus Durumu */
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus, 
    .stSelectbox div[data-baseweb="select"] > div:focus-within, 
    .stMultiSelect div[data-baseweb="select"] > div:focus-within {
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
    
    /* Formdaki Temel Bilgiler başlığındaki ikonlar */
    h4 .icon {
        color: #00D285; /* İkon rengi */
        font-size: 1.5rem; /* İkon boyutu */
    }


    /* SUBTITLE (Alt Başlık) */
    .subtitle {
        color: #718096;
        text-align: center;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    /* "DEVAM ET" ve "PROGRAMI OLUŞTUR" BUTONLARI (Görseldeki Yeşil Geniş Buton) */
    .stButton > button[data-testid*="stFormSubmitButton"] { /* Sadece form submit butonları */
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
    .stButton > button[data-testid*="stFormSubmitButton"]:hover {
        background-color: #00C07A !important; /* Hover Açık Yeşil */
        transform: translateY(-1px);
    }
    
    /* "GERİ" BUTONU (Görseldeki Gri Buton) */
    .stButton > button[kind="secondary"] { /* Streamlit'in kendi secondary butonu */
        background-color: #2D3748 !important; /* Gri ton */
        color: #E0E0E0 !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        padding: 0.75rem 1rem;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #4A5568 !important; /* Hover koyu gri */
        transform: translateY(-1px);
    }

    /* Genel Diğer Butonlar (Tab içindekiler gibi) */
    .stButton > button:not([data-testid*="stFormSubmitButton"]):not([kind="secondary"]) {
        background-color: #1A202C !important; /* Koyu gri */
        color: #00D285 !important;
        border: 1px solid #00D285 !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stButton > button:not([data-testid*="stFormSubmitButton"]):not([kind="secondary"]):hover {
        background-color: #00D285 !important;
        color: #0E121B !important;
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
if "current_page" not in st.session_state: # Çoklu form için sayfa durumu
    st.session_state.current_page = 1 # 1: Temel Bilgiler, 2: Hedef ve Deneyim, 3: Sağlık ve Yaşam Tarzı

# --- 4. API ANAHTARI KONTROLÜ ---
try:
    api_key = st.secrets["google_apikey"]
except:
    api_key = None

# ==================================================
# MOD 1: ONBOARDING (GÖRSELDEKİ ÇOK ADIMLI FORM EKRANI)
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
        
        # Görseldeki Pagination Dots (Aktif/Pasif durumları dinamik)
        active_dot = '<div style="width: 20px; height: 4px; background-color: #00D285; border-radius: 2px;"></div>'
        inactive_dot = '<div style="width: 6px; height: 4px; background-color: #2D3748; border-radius: 2px;"></div>'
        
        dots_html = "<div style='display: flex; justify-content: center; gap: 5px; margin-bottom: 30px;'>"
        for i in range(1, 4): # 3 sayfa olduğu için
            if i == st.session_state.current_page:
                dots_html += active_dot
            else:
                dots_html += inactive_dot
        dots_html += "</div>"
        st.markdown(dots_html, unsafe_allow_html=True)

        # --- FORM BAŞLANGICI ---
        with st.form("onboarding_form", clear_on_submit=False): # Sayfa değişiminde formun sıfırlanmaması için
            
            # --- SAYFA 1: TEMEL BİLGİLER ---
            if st.session_state.current_page == 1:
                st.markdown('<h4 style="color:white;"><span class="icon">📝</span> Temel Bilgiler</h4>', unsafe_allow_html=True)
                
                name = st.text_input("İsim", placeholder="Adınız", key="name_input")
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) 

                c1, c2 = st.columns(2)
                with c1:
                    age = st.number_input("Yaş", min_value=10, max_value=90, value=25, key="age_input")
                with c2:
                    gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın", "Belirtmek İstemiyorum"], key="gender_input")
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) 

                c3, c4 = st.columns(2)
                with c3:
                    height = st.number_input("Boy (cm)", min_value=100, max_value=250, value=175, key="height_input")
                with c4:
                    weight = st.number_input("Kilo (kg)", min_value=30, max_value=200, value=75, key="weight_input")
                st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True) 

                col_b1, col_b2 = st.columns([1, 1])
                with col_b2:
                    if st.form_submit_button("Devam Et ➔", type="primary"):
                        if name:
                            st.session_state.user_data.update({
                                "name": name, "age": age, "gender": gender,
                                "height": height, "weight": weight
                            })
                            st.session_state.current_page = 2
                            st.rerun()
                        else:
                            st.error("Lütfen adınızı giriniz.")

            # --- SAYFA 2: HEDEF VE DENEYİM ---
            elif st.session_state.current_page == 2:
                st.markdown('<h4 style="color:white;"><span class="icon">💪</span> Hedef ve Deneyim</h4>', unsafe_allow_html=True)
                
                goal = st.text_area("Ana Hedefin Nedir?", placeholder="Örn: Yağ oranımı %12'ye düşürmek istiyorum, kas kütlemi artırmak istiyorum...", height=100, key="goal_input")
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    fitness_level = st.selectbox("Deneyim", ["Yeni Başlayan (0-6 ay)", "Orta (6-24 ay)", "İleri (2+ yıl)"], key="fitness_level_input")
                with c2:
                    equipment = st.multiselect("Ekipman", ["Spor Salonu (Tam)", "Dumbbell", "Barbell", "Direnç Bandı", "Vücut Ağırlığı", "TRX", "Koşu Bandı"], key="equipment_input")
                st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.form_submit_button("Geri", type="secondary"):
                        st.session_state.current_page = 1
                        st.rerun()
                with col_b2:
                    if st.form_submit_button("Devam Et ➔", type="primary"):
                        if goal:
                            st.session_state.user_data.update({
                                "goal": goal, "fitness_level": fitness_level, "equipment": equipment
                            })
                            st.session_state.current_page = 3
                            st.rerun()
                        else:
                            st.error("Lütfen ana hedefinizi giriniz.")

            # --- SAYFA 3: SAĞLIK VE YAŞAM TARZI ---
            elif st.session_state.current_page == 3:
                st.markdown('<h4 style="color:white;"><span class="icon">❤️</span> Sağlık ve Yaşam Tarzı</h4>', unsafe_allow_html=True)
                
                injuries = st.text_input("Sakatlık veya Sağlık Sorunu", placeholder="Yok", key="injuries_input")
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    sleep_hours = st.number_input("Günlük Uyku (Saat)", min_value=4, max_value=12, value=7, key="sleep_hours_input")
                with c2:
                    stress_level = st.selectbox("Stres Seviyesi", ["Düşük", "Orta", "Yüksek"], key="stress_level_input")
                st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.form_submit_button("Geri", type="secondary"):
                        st.session_state.current_page = 2
                        st.rerun()
                with col_b2:
                    if st.form_submit_button("Programı Oluştur", type="primary"):
                        st.session_state.user_data.update({
                            "injuries": injuries, "sleep_hours": sleep_hours, "stress_level": stress_level
                        })
                        st.session_state.profile_complete = True
                        st.rerun()

        st.markdown('<div class="footer">Powered by Gemini 2.5 Flash & HAS Team Methodology</div>', unsafe_allow_html=True)

# ==================================================
# MOD 2: ANA UYGULAMA (SOHBET & PROGRAMLAR)
# ==================================================
else:
    user = st.session_state.user_data
    
    # --- AI MODEL AYARLARI & PROMPT (Detaylı Prompt) ---
    system_instruction = f"""
    Sen bir HAS Team kişisel antrenörüsün. Amacın, kullanıcıdan aldığı verilere göre bilimsel, kişisel, sürdürülebilir fitness ve beslenme planları hazırlamaktır. Ayrıca, kullanıcının programı gerçekten uygulayıp uygulamadığını ölçmek ve veriye dayalı adaptasyonlar yapmak için haftalık takip sistemiyle destek sun. Motivasyonel, profesyonel ve kapsayıcı bir dil kullan. HAS Team’in bilimsel, sürdürülebilir ve kişisel gelişimi önceleyen değerleriyle hareket et.

    KULLANICI PROFİLİ:
    - İsim: {user.get('name')} ({user.get('gender')}, {user.get('age')} yaş)
    - Fiziksel: {user.get('height')}cm, {user.get('weight')}kg
    - Ana Hedef: {user.get('goal')}
    - Deneyim Seviyesi: {user.get('fitness_level')}
    - Ekipman Erişimi: {', '.join(user.get('equipment')) if user.get('equipment') else 'Yok'}
    - Sakatlık/Sağlık Durumu: {user.get('injuries') if user.get('injuries') else 'Yok'}
    - Günlük Uyku: {user.get('sleep_hours')} saat
    - Stres Seviyesi: {user.get('stress_level')}

    KURALLAR:
    1. Bu verilere dayanarak kişiye özel tavsiye ver.
    2. Kullanıcının sakatlığı varsa egzersizleri ona göre uyarla.
    3. Motivasyonel ama ciddiyetsiz olmayan bir dil kullan.
    4. Cevaplarını Markdown formatında düzenli ver (Tablolar, Bullet pointler, kalın yazılar).
    5. Çıktılarda HTML/CSS kodu asla gösterme.
    6. Antrenman programı isterse: Haftalık antrenman sıklığına göre (genellikle 3-5 gün) split sistemi (Full Body, Upper/Lower, Push/Pull/Legs) öner, her gün için egzersiz adı, set, tekrar, RPE veya ağırlık, tempo (örn. 3010), dinlenme süresi belirt. Progresyon stratejisi ekle.
    7. Beslenme programı isterse: Kullanıcının kilosuna, yaşına, cinsiyetine ve hedefine (kilo verme, kas kazanımı) göre günlük kalori ve makro (protein, yağ, karbonhidrat) dağılımını hesapla (Mifflin-St Jeor denklemi kullanılabilir). Ardından 1 günlük örnek bir menü sun (öğünlere ayrılmış). Hidrasyon önerisi (örn. 30-35 ml/kg) ekle.
    8. Supplement önerisi isterse: Sadece kanıta dayalı, güvenli ve hedefe uygun takviyeler öner (Kreatin, Omega-3, D Vitamini, Kafein vb.). Her öneri için bilimsel gerekçe, dozaj, zamanlama ve basit bir açıklama sun.
    9. Takip ve Motivasyon: Her etkileşimde kullanıcının ilerlemesini sor, hedeflerini hatırlat ve küçük adımların önemini vurgula. Haftalık uyum raporu doldurmasını öner.
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 AI Koç", "🏋️ Antrenman", "🍎 Beslenme", "💊 Supplement", "👤 Profil"])

        # --- TAB 1: AI KOÇ (SOHBET) ---
        with tab1:
            if not st.session_state.messages:
                initial_msg = f"Selam {user.get('name')}! Profilini detaylıca inceledim ve hedefin olan **{user.get('goal').lower()}** için tam gaz hazırız! Sana nasıl yardımcı olabilirim? Antrenman programı mı istersin, beslenme önerisi mi, yoksa motivasyonel bir sohbet mi?"
                st.session_state.messages.append({"role": "model", "content": initial_msg})
            
            for message in st.session_state.messages:
                role = "user" if message["role"] == "user" else "assistant"
                with st.chat_message(role):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Koçuna bir soru sor..."):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                try:
                    chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages])
                    response = chat.send_message(prompt)
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
                    st.session_session.messages.append({"role": "model", "content": response.text})
                except Exception as e:
                    st.error(f"Üzgünüm, bir hata oluştu: {e}")

        # --- TAB 2: ANTRENMAN ---
        with tab2:
            st.info(f"🏋️ {user.get('name')}, hedefin **{user.get('goal').lower()}** doğrultusunda sana özel bir antrenman programı hazırlayabilirim. Mevcut ekipmanların: **{', '.join(user.get('equipment')) if user.get('equipment') else 'Vücut Ağırlığı (Ekipman belirtilmemiş)'}**.")
            
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                gun_sayisi = st.slider("Haftada kaç gün antrenman yapmak istersin?", 1, 7, 3, key="antrenman_gun_sayisi")
            with col_t2:
                split_type = st.selectbox("Antrenman bölünmesi (Split)", ["Full Body", "Upper/Lower", "Push/Pull/Legs", "Bölgesel Odaklı"], key="split_type_select")
            
            st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

            if st.button("Antrenman Programını Oluştur"):
                with st.spinner("Programın oluşturuluyor, birazdan hazır! 💪"):
                    req = f"""
                    Kullanıcının profil bilgileri: {user}.
                    Haftada {gun_sayisi} gün antrenman yapacak.
                    Tercih ettiği split tipi: {split_type}.
                    Mevcut ekipmanları: {', '.join(user.get('equipment')) if user.get('equipment') else 'Vücut ağırlığı'}.
                    Sakatlık durumu: {user.get('injuries') if user.get('injuries') else 'Yok'}.
                    Bu bilgilere göre, {user.get('goal')} hedefine uygun, detaylı ve açıklayıcı bir haftalık antrenman programı oluştur.
                    Her egzersiz için set, tekrar aralığı, RPE/Tempo bilgisi ve dinlenme süresi belirt.
                    Programın başına kısa bir açıklama ve progresyon stratejisi ekle.
                    """
                    res = model.generate_content(req)
                    st.markdown(res.text)

        # --- TAB 3: BESLENME ---
        with tab3:
            st.info(f"🍎 {user.get('name')}, kilon ({user.get('weight')}kg) ve hedefin **{user.get('goal').lower()}** doğrultusunda kişiye özel bir beslenme planı ve makro önerileri sunabilirim.")
            
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
            if st.button("Günlük Beslenme Planı Oluştur"):
                with st.spinner("Kalori ve makrolar hesaplanıyor, menü hazırlanıyor... 🥗"):
                    req = f"""
                    Kullanıcının profil bilgileri: {user}.
                    Hedefi: {user.get('goal')}.
                    Yaş: {user.get('age')}, Boy: {user.get('height')}cm, Kilo: {user.get('weight')}kg, Cinsiyet: {user.get('gender')}.
                    Bu verilere dayanarak, Mifflin-St Jeor denklemini kullanarak günlük kalori ihtiyacını (TDEE) hesapla.
                    Hedefine uygun (cut/maintenance/bulk) bir plan belirle.
                    Makro besin dağılımını (protein g/kg, yağ g/kg, karbonhidrat kalan kalori) öner.
                    Ardından, 1 günlük örnek bir menü oluştur (Kahvaltı, Ara Öğün, Öğle Yemeği, Ara Öğün, Akşam Yemeği) ve her öğündeki besinleri ve porsiyonları belirt.
                    Hidrasyon önerisi (örn. {round(user.get('weight') * 35 / 1000, 1)} - {round(user.get('weight') * 40 / 1000, 1)} litre su) ekle.
                    """
                    res = model.generate_content(req)
                    st.markdown(res.text)

        # --- TAB 4: SUPPLEMENT ---
        with tab4:
            st.info(f"💊 {user.get('name')}, **{user.get('goal').lower()}** hedefine ve mevcut durumuna göre bilimsel kanıtlarla desteklenmiş takviye önerileri sunabilirim. Unutma, takviyeler sadece destekleyici olmalıdır.")
            
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

            if st.button("Supplement Önerilerini Gör"):
                with st.spinner("Bilimsel veriler taranıyor, öneriler hazırlanıyor... 🧪"):
                    req = f"""
                    Kullanıcının profil bilgileri: {user}.
                    Hedefi: {user.get('goal')}.
                    Bu hedefe ve profiline uygun, kanıta dayalı ve güvenli takviye önerilerinde bulun.
                    Her takviye için:
                    - Takviye Adı
                    - Bilimsel Gerekçe (Kısa ve öz)
                    - Önerilen Dozaj ve Zamanlama
                    - Basit Açıklama (Kullanıcının anlayacağı dilde)
                    Sadece kreatin, omega-3, D vitamini, beta-alanin, kafein gibi yaygın ve etkili takviyeleri değerlendir. "Fat burner" gibi kanıtı zayıf ürünlerden kaçın.
                    """
                    res = model.generate_content(req)
                    st.markdown(res.text)
        
        # --- TAB 5: PROFİL ---
        with tab5:
            st.success("Kayıtlı Profil Bilgilerin")
            # st.json(user) # JSON
