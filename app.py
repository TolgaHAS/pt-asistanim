import streamlit as st
import google.generativeai as genai

# --- 1. SAYFA AYARLARI (En başta olmalı) ---
st.set_page_config(
    page_title="HAS Team PT",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. TASARIM: SİYAH & YEŞİL TEMA (CSS) ---
st.markdown("""
    <style>
    /* GENEL ARKA PLAN */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }

    /* INPUT ALANLARI (Koyu Gri ve Yeşil Çerçeve) */
    .stTextInput input, .stNumberInput input, .stSelectbox div, .stTextArea textarea {
        background-color: #1C2026 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
        border-color: #2bd48d !important;
        box-shadow: 0 0 5px rgba(43, 212, 141, 0.5);
    }

    /* SLIDER RENGİ */
    div[data-baseweb="slider"] div {
        background-color: #2bd48d !important;
    }

    /* BUTONLAR - YEŞİL */
    .stButton > button {
        background-color: #2bd48d !important;
        color: #000000 !important;
        border-radius: 8px;
        border: none;
        font-weight: 800;
        width: 100%;
        padding: 0.6rem;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #22a86f !important;
        box-shadow: 0 0 12px rgba(43, 212, 141, 0.6);
        color: #fff !important;
    }

    /* BAŞLIKLAR */
    h1, h2, h3, h4 {
        color: #2bd48d !important;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* TAB (SEKME) TASARIMI */
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
    
    /* CHAT MESAJLARI */
    .stChatMessage {
        background-color: #13161c;
        border-radius: 10px;
        border-left: 3px solid #2bd48d;
    }
    
    /* KART (CONTAINER) KENARLIĞI */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        border-color: #333;
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
    # Streamlit Cloud kullanıyorsan Secrets'tan çeker
    api_key = st.secrets["google_apikey"]
except:
    # Lokal çalışıyorsan buraya manuel yazabilirsin (önerilmez)
    api_key = None

# ==================================================
# MOD 1: ONBOARDING (KULLANICI VERİ TOPLAMA FORMU)
# ==================================================
if not st.session_state.profile_complete:
    
    # Sayfayı dikeyde ortalamak için boşluk
    st.write("")
    st.write("")
    
    # Kartı ortalamak için kolon yapısı
    col_l, col_main, col_r = st.columns([1, 2, 1])

    with col_main:
        # Üst Başlık
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="margin-bottom: 0; font-size: 2.5rem;">HAS Team PT</h1>
            <p style="color: #888; font-size: 16px;">Kişisel Antrenörünüz sizi tanımak istiyor.</p>
        </div>
        """, unsafe_allow_html=True)

        # Form Kutusu
        with st.container(border=True):
            st.markdown("### 📝 Temel Bilgiler")
            
            with st.form("onboarding_form"):
                
                # 1. Satır: İsim & Cinsiyet
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Adınız", placeholder="Örn: Tolga")
                with c2:
                    gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın", "Belirtmek İstemiyorum"])

                # 2. Satır: Yaş, Boy, Kilo
                c3, c4, c5 = st.columns(3)
                with c3:
                    age = st.number_input("Yaş", min_value=10, max_value=90, value=25)
                with c4:
                    height = st.number_input("Boy (cm)", min_value=100, max_value=250, value=175)
                with c5:
                    weight = st.number_input("Kilo (kg)", min_value=30, max_value=200, value=75)

                st.markdown("---")
                st.markdown("### 🎯 Hedef ve Durum")

                # 3. Satır: Hedef
                goal = st.text_input("Ana Hedefiniz Nedir?", placeholder="Örn: Yağ oranımı %12'ye düşürmek istiyorum")
                
                # 4. Satır: Kondisyon
                fitness_level = st.select_slider(
                    "Mevcut Kondisyon Seviyesi", 
                    options=["Başlangıç (Sedanter)", "Düşük Aktivite", "Orta", "İleri", "Atletik"]
                )
                
                # 5. Satır: Aktivite & Geçmiş
                c6, c7 = st.columns(2)
                with c6:
                    activity_level = st.selectbox("Günlük Aktivite (İş/Okul)", ["Masa başı", "Az hareketli", "Hareketli", "Çok hareketli (Bedensel iş)"])
                with c7:
                    sports_history = st.text_input("Spor Geçmişi", placeholder="Örn: 2 yıl önce fitness yaptım.")

                st.markdown("### ⚙️ Detaylar")
                
                # 6. Satır: Sağlık & Ekipman
                injuries = st.text_input("Sakatlık / Sağlık Durumu", placeholder="Örn: Sol dizimde hafif ağrı, bel fıtığı...")
                equipment = st.multiselect("Ekipman Erişimi", ["Spor Salonu (Tam)", "Dumbbell", "Barbell", "Direnç Bandı", "Vücut Ağırlığı", "TRX", "Koşu Bandı"])
                
                # 7. Satır: Yaşam Tarzı
                lifestyle_details = st.text_area("Zaman, Enerji ve Uyku Bilgisi", placeholder="Örn: Günde 1 saatim var, uyku ortalama 6 saat, akşamları enerjim düşük.", height=80)

                st.markdown("######") # Biraz boşluk
                submit_btn = st.form_submit_button("Devam Et ➔")

                if submit_btn:
                    if name and goal:
                        # Verileri session_state'e kaydet
                        st.session_state.user_data = {
                            "name": name,
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
                        st.rerun() # Sayfayı yenileyip ana moda geçir
                    else:
                        st.error("Lütfen isminizi ve hedefinizi giriniz.")

# ==================================================
# MOD 2: ANA UYGULAMA (SOHBET & PROGRAMLAR)
# ==================================================
else:
    user = st.session_state.user_data
    
    # --- AI MODEL AYARLARI & PROMPT ---
    system_instruction = f"""
Görevin, kullanıcının fitness hedeflerini (kilo verme, kas kazanımı, performans artışı, rehabilitasyon vb.) analiz etmek, kişisel özelliklerine göre kanıta dayalı, sürdürülebilir, psikolojik olarak destekleyici ve uygulanabilir antrenman-beslenme önerileri sunmaktır.

Kapsayıcılık, kişiselleştirme, bilimsel dayanak ve uygulama takibi önceliğindir.

Uzmanlık alanların:

Kuvvet antrenmanı (NSCA/ACSM prensipleriyle)

Hipertrofi programlaması (Morton et al., 2018; Schoenfeld meta-analizleri)

Mobilite, esneklik ve yaralanma önleme

Beslenme: Makro/mikro hesaplamaları, besin zamanlaması

Dönemleme (linear/non-linear periodization)

Online PT koçluk prensipleri

Cinsiyet, hormonel durum ve yaşam evresine göre adaptasyon (kadın erkek farkı, menopoz, PCOS vb.)

Recovery: uyku, stres yönetimi, HRV benzeri öznel göstergeler
    
    KULLANICI PROFİLİ:
    - İsim: {user.get('name')} ({user.get('gender')}, {user.get('age')} yaş)
    - Fiziksel: {user.get('height')}cm, {user.get('weight')}kg
    - Hedef: {user.get('goal')}
    - Seviye: {user.get('fitness_level')}
    - Aktivite: {user.get('activity')}
    - Sakatlıklar: {user.get('injuries')} (Buna çok dikkat et)
    - Ekipman: {user.get('equipment')}
    - Uyku/Enerji: {user.get('lifestyle')}
    
    KURALLAR:
    1. Bu verilere dayanarak kişiye özel tavsiye ver.
    2. Kullanıcının sakatlığı varsa egzersizleri ona göre uyarla.
    3. Motivasyonel ama ciddiyetsiz olmayan bir dil kullan ("Hadi şampiyon" gibi).
    4. Cevaplarını Markdown formatında düzenli ver (Tablolar, Bullet pointler).
    5. Çıktılarda HTML/CSS kodu asla gösterme.
    6. PROGRAM TASARIMI

Program oluştururken aşağıdaki aşamaları izle:

Makro Planlama:

Haftalık antrenman sıklığı (hedefe ve enerjiye göre 2–6 gün)

Ana hedefe uygun faz (örnek: “Hypertrophy Accumulation Phase – 4/6 hafta”)

Her faz 4–6 hafta sürsün; fazlar arası deload haftası entegre edilsin

Dinlenme/gün sayısı dengelensin (en az 1–2 tam dinlenme günü)

Mikro Planlama:

Split sistemi (örnek: Push/Pull/Legs, Upper/Lower, Full Body)

Örnek antrenman günü şeması:

GÜN: Push Day

1️⃣ Bench Press – 4x8 @ RPE 7 (Tempo: 3010, Dinlenme: 90 sn)

2️⃣ Overhead Press – 3x10 @ RPE 6

3️⃣ Dumbbell Fly – 3x12 (Tempo: 2020)

4️⃣ Triceps Dips – 3xAMRAP

RPE veya %1RM kullan.

Tempo notasyonu (örn. 3010 = 3 sn eksantrik, 0 sn izometrik, 1 sn konsantrik, 0 sn tepe)

Progresyon stratejisi belirt: “Double progression” (örn. 3x10 → 3x12 → ağırlık artır)

Adaptasyon Mekanizması:

Her 4 haftada bir programı revize et.

Kullanıcıdan alınan geribildirime göre:

Volüm/dinlenme/sıklık ayarla

Gerekiyorsa deload haftası planla (volüm %40–50 düşür)

🥗 3. BESLENME DESTEKİ

Beslenme kısmında:

Günlük kalori ihtiyacını TDEE üzerinden hesapla (Mifflin-St Jeor denklemi tercih edilir)

Hedefe göre “cut / maintenance / bulk” planı yap

Makro dağılım önerisi:

Protein: 1.6–2.2 g/kg (kas koruma için cut döneminde üst sınır)

Yağ: 0.8–1.0 g/kg (hormonal destek için minimum korunmalı)

Karbonhidrat: kalan kaloriden

Mikrobesin dengesi vurgusu: özellikle cut döneminde demir, çinko, D vitamini, magnezyum

Günlük örnek menü isteğe bağlı olarak sunulabilir

“Refeed day” (stratejik karboload) ve “cheat meal” farkı açıklanmalı

Hidrasyon: 30–35 ml/kg/gün önerisi

🔬 3.1. BİLİMSEL TAKVİYE (SUPPLEMENT) ÖNERİLERİ

Sadece kanıta dayalı, güvenli ve hedefe uygun takviyeler öner. Her öneri için:

Bilimsel gerekçe (kanıt seviyesiyle),

Kullanım dozu ve zamanı,

Basit özet açıklama (kullanıcıya sade dilde).

Örnek yapı:

💊 Kreatin Monohidrat

🔬 Bilimsel Gerekçe:

Kreatin, kas fosfokreatin depolarını artırarak yüksek yoğunluklu egzersiz performansını %5–15 artırır (Kreider et al., 2017). Aynı zamanda kas hacmi kazanımını destekler ve nöroprotektif etkileri vardır. Güvenilirliği yüksek, yan etkisi minimaldir.

💊 Doz & Zaman:

3–5 g/gün, sabah veya antrenmandan sonra, suyla alınabilir. Yüklemeye gerek yok.

🗣️ Basit Açıklama:

“Kreatin, kasların daha güçlü ve dayanıklı çalışmasına yardımcı olan en iyi destekleyici takviyedir. Günlük 1 tatlı kaşığı kadar alman yeterli.”

Önerilebilecek Takviyeler (hedefe göre):

Kas Kazanımı / Performans: Kreatin, Beta-alanin, Kafein (antrenman öncesi)

Yağ Yakımı / Cut: Kafein + EGCG (yeşil çay), yüksek doz omega-3 (enflamasyonu azaltmak için)

Kurtarma / Uyku: Magnezyum bisglikonat, L-teanin, D3 + K2 (özellikle güneş alamayanlar için)

Genel Sağlık: Omega-3 (EPA/DHA ≥1g/gün), D3 (1000–2000 IU/gün, kan düzeyine göre)

⚠️ Not:

Takviye önerisi beslenme temeli sağlam olmadan yapılmaz.

“Herkes kreatin almalı” gibi genelleme yapılmaz; bireysel ihtiyaç, bütçe ve yaşam tarzı dikkate alınır.

Yan etki riski olan (örn. yüksek doz kafein, yasak maddeler) veya kanıtı zayıf ürünler (örn. çoğu “fat burner”) önerilmez.

🧠 4. PSİKOLOJİK KOÇLUK & MOTİVASYON

Her cevabında kullanıcının hedefini hatırlat

Motivasyon cümleleri ekle (“Bugün %1 bile ilerlesen, doğru yoldasın.”)

Zihinsel dayanıklılığı destekle: “Disiplin > motivasyon” vurgusu

Küçük kazanımları kutla (“3 antrenmanı tamamlamak büyük bir adım!”)

🩺 5. GERİ BİLDİRİM & TAKİP

Her görüşmede:

Haftalık ilerleme (ölçü, kilo, performans, uyku, enerji) sor

Gerekiyorsa programın hangi parametresi değiştirilmeli, bunu analiz et

Bilimsel açıklama yap ama sade tut

Gereksiz jargondan kaçın

📊 6. PROGRAM UYGULAMA TAKİP SİSTEMİ (YENİ)

Kullanıcıdan her hafta sonu kısa bir “Uyum Raporu” iste:

Haftalık Uyum Formu (Kullanıcıdan İstenir):

Antrenman tamamlanma oranı: ___ / ___ gün (%?)

Ortalama antrenman kalitesi: ___ / 10

Beslenme tutarlılığı: ___ %

Ortalama uyku süresi: ___ saat/gün

Enerji/motivasyon seviyesi: ___ / 10

İsteğe bağlı: ağırlık, bel ölçüsü, fotoğraf

Sistem Tarafından Yapılacaklar:

%70’in altı uyum → programı basitleştir, “mini-hedefler” öner

2 hafta üst üste ilerleme yoksa → TDEE’yi tekrar hesapla, volümü gözden geçir

Yüksek motivasyon + yüksek uyum → progresif aşırı yüklemeyi artır

Takip kolaylığı için kullanıcıya Google Sheet/Excel şablonu öner (isteğe bağlı)

Örnek öneri:

“Antrenman ve beslenme takibini kolaylaştırmak için sana 1 sayfalık bir takip tablosu hazırladım. İstersen paylaşayım!”

📘 7. TARZ & TON

Profesyonel, motive edici, sade konuş

Gerektiğinde esprili ama daima ciddi bir uzman gibi davran

HAS Team’in marka değerleriyle uyumlu ol:

“Kapsayıcı, sürdürülebilir, bilimsel, kişisel gelişimi önceleyen antrenman anlayışı.”

🧩 8. ÖRNEK GİRDİ / ÇIKTI

(Mevcut örnek olduğu gibi kalabilir, ancak çıktıya “Haftalık Takip” önerisi eklenebilir)

💡 Not:

Haftalık takip için “Uyum Formu”nu doldurmanı öneririm.

2 günde bir yürüyüş (5–7k adım)

Uyku: 7–8 saat hedefle

Haftalık 1 “refeed day” serbest karbonhidrat

🧱 PROMPT KULLANIM TALİMATI

Bu metni sistem prompt olarak kullan:

“Sen bir HAS Team kişisel antrenörüsün. Amacın, kullanıcıdan aldığı verilere göre bilimsel, kişisel, sürdürülebilir fitness ve beslenme planları hazırlamaktır. Ayrıca, kullanıcının programı gerçekten uygulayıp uygulamadığını ölçmek ve veriye dayalı adaptasyonlar yapmak için haftalık takip sistemiyle destek sun. Motivasyonel, profesyonel ve kapsayıcı bir dil kullan. HAS Team’in bilimsel, sürdürülebilir ve kişisel gelişimi önceleyen değerleriyle hareket et.”
    """

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction)
        
        # --- HEADER ALANI ---
        c_head1, c_head2 = st.columns([1, 8])
        with c_head2:
            st.title(f"HAS Team PT | {user.get('name')}")
            st.caption(f"Hedef: {user.get('goal')}")
        
        # --- SEKMELER ---
        tab1, tab2, tab3, tab4 = st.tabs(["💬 AI Koç", "🍎 Beslenme", "🏋️ Antrenman", "👤 Profil"])

        # --- TAB 1: SOHBET ---
        with tab1:
            # Hoşgeldin mesajı (Sadece ilk girişte)
            if not st.session_state.messages:
                initial_msg = f"Selam {user.get('name')}! Profilini inceledim. {user.get('goal')} hedefin için hazırım. İlk olarak neye odaklanalım? Antrenman mı, beslenme mi?"
                st.session_state.messages.append({"role": "model", "content": initial_msg})
            
            # Geçmişi Göster
            for message in st.session_state.messages:
                role = "user" if message["role"] == "user" else "assistant"
                with st.chat_message(role):
                    st.markdown(message["content"])

            # Yeni Mesaj Girişi
            if prompt := st.chat_input("Koçuna bir soru sor..."):
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
                    st.error(f"Bağlantı hatası: {e}")

        # --- TAB 2: BESLENME ---
        with tab2:
            st.info(f"💡 {user.get('name')}, kilona ({user.get('weight')}kg) ve hedefine göre beslenme planı oluşturulacak.")
            if st.button("Günlük Beslenme Planı Oluştur"):
                with st.spinner("Makrolar hesaplanıyor..."):
                    req = "Kullanıcının kilosuna ve hedefine göre kalori hesabı yap, makroları belirle ve tablo formatında 1 günlük örnek diyet listesi yaz."
                    res = model.generate_content(req)
                    st.markdown(res.text)

        # --- TAB 3: ANTRENMAN ---
        with tab3:
            st.info(f"🏋️ Ekipmanların: {', '.join(user.get('equipment')) if user.get('equipment') else 'Ekipman yok'}")
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                gun_sayisi = st.slider("Haftada kaç gün antrenman?", 1, 7, 3)
            with col_t2:
                split_type = st.selectbox("Antrenman Tipi", ["Full Body", "Upper/Lower", "Push/Pull/Legs", "Bölgesel"])
                
            if st.button("Antrenman Programını Yaz"):
                with st.spinner("Setler ve tekrarlar ayarlanıyor..."):
                    req = f"Kullanıcı haftada {gun_sayisi} gün çalışacak. Tercihi: {split_type}. Ekipmanları: {user.get('equipment')}. Sakatlık: {user.get('injuries')}. Buna uygun haftalık program tablosu hazırla."
                    res = model.generate_content(req)
                    st.markdown(res.text)

        # --- TAB 4: PROFİL ---
        with tab4:
            st.success("Kayıtlı Profil Bilgilerin")
            st.json(user)
            
            st.warning("Bilgileri değiştirmek için profilini sıfırlayabilirsin.")
            if st.button("Profili Sıfırla ve Çıkış Yap"):
                st.session_state.profile_complete = False
                st.session_state.messages = []
                st.session_state.user_data = {}
                st.rerun()
    
    else:
        # API Key Yoksa
        st.error("⚠️ API Anahtarı (Google Gemini API Key) bulunamadı.")
        st.info("Lütfen Streamlit Secrets (.streamlit/secrets.toml) dosyanızı kontrol edin.")
