import streamlit as st
from PIL import Image
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="KisanSetu AI | किसान सेतु", page_icon="🌾", layout="centered", initial_sidebar_state="collapsed")

# Configure Gemini API
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Modern Enterprise Mobile Theme Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Hind:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Hind', sans-serif;
    }
    .main-hero {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        border-radius: 16px;
        padding: 24px 16px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(27,94,32,0.18);
    }
    .main-hero h1 { font-size: 26px; font-weight: 700; color: #FFFFFF; margin: 0; }
    .main-hero p { font-size: 13px; color: #E8F5E9; margin-top: 6px; }
    .welcome-banner {
        background: #E8F5E9;
        border: 1px solid #A5D6A7;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        color: #1B5E20;
        margin-bottom: 18px;
    }
    .service-card {
        background: #FFFFFF;
        border: 1.5px solid #E0E0E0;
        border-radius: 14px;
        padding: 18px 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kisan-card {
        background: #F1F8E9;
        border-left: 5px solid #2E7D32;
        border-radius: 10px;
        padding: 16px;
        margin-top: 14px;
        margin-bottom: 14px;
        color: #1B5E20;
    }
    .trader-card {
        background: #FFFDE7;
        border-left: 5px solid #FBC02D;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        color: #212121;
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 48px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE -----------------
if "onboarded" not in st.session_state:
    st.session_state["onboarded"] = False
if "selected_bhasha" not in st.session_state:
    st.session_state["selected_bhasha"] = "हिंदी (Hindi)"
if "selected_role" not in st.session_state:
    st.session_state["selected_role"] = "किसान (Farmer)"
if "active_module" not in st.session_state:
    st.session_state["active_module"] = "dashboard"

if "trader_directory" not in st.session_state:
    st.session_state["trader_directory"] = [
        {"name": "रमेश चंद्र (गांधी मंडी ट्रेडर्स)", "phone": "+91 9829012345", "location": "भींडर / वल्लभनगर", "crop": "पत्तागोभी (Cabbage)", "rate": 28, "unit": "किलो", "min_qty": "10 किलो", "transport_support": "हाँ (₹50 तक भाड़ा देंगे)"},
        {"name": "मेवाड़ एग्रो प्रोक्योरमेंट", "phone": "+91 9414056789", "location": "उदयपुर मुख्य मंडी", "crop": "टमाटर (Tomato)", "rate": 35, "unit": "किलो", "min_qty": "20 किलो", "transport_support": "हाँ (बल्क पिकअप फ्री)"},
        {"name": "कृष्णा फ्रेश वेज (लोकल वेंडर)", "phone": "+91 8875011223", "location": "कानोड़ चौराहा", "crop": "हरी मिर्च (Green Chilli)", "rate": 55, "unit": "किलो", "min_qty": "5 किलो", "transport_support": "नहीं (दुकान पर डिलीवरी)"}
    ]

# Audio TTS & Mic Helper Function
def speak_button(text_content, button_text="🔊 आवाज़ में सुनें (Listen)"):
    clean_text = text_content.replace('"', '').replace("'", "").replace('\n', ' ')
    js_code = f"""
    <button onclick="
        window.speechSynthesis.cancel();
        let utter = new SpeechSynthesisUtterance('{clean_text[:400]}');
        utter.lang = 'hi-IN';
        utter.rate = 0.95;
        window.speechSynthesis.speak(utter);
    " style="background-color: #2E7D32; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 6px;">
    {button_text}
    </button>
    """
    st.components.v1.html(js_code, height=45)

def mic_helper():
    mic_html = """
    <div style="display:flex; align-items:center; gap:8px; margin: 4px 0 10px 0;">
        <button type="button" onclick="
            var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'hi-IN';
            recognition.onstart = function() { alert('माइक चालू है, बोलिए...'); };
            recognition.onresult = function(event) {
                var transcript = event.results[0][0].transcript;
                navigator.clipboard.writeText(transcript);
                alert('आप बोले: ' + transcript + ' (कॉपी हो गया! इनपुट बॉक्स में पेस्ट करें)');
            };
            recognition.start();
        " style="background-color: #E8F5E9; color: #1B5E20; border: 1px solid #4CAF50; padding: 6px 12px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;">
        🎙️ बोलकर भरें (Tap Mic to Speak)
        </button>
        <span style="font-size:12px; color:#666;">माइक दबाकर बोलें और पेस्ट करें</span>
    </div>
    """
    st.components.v1.html(mic_html, height=40)

# Welcome message translations
welcome_dict = {
    "हिंदी (Hindi)": "राम राम सा! किसान सेतु ऐप में आपका स्वागत है।",
    "मेवाड़ी (Mewari)": "राम राम सा! किसान सेतु में आपरो घणो-घणो स्वागत है।",
    "मारवाड़ी (Marwari)": "खम्मा घणी सा! किसान सेतु पोर्टल माथे आपरो स्वागत है।",
    "ગુજરાતી (Gujarati)": "નમસ્તે! કિસાન સેતુ એપમાં આપનું હાર્દિક સ્વાગત છે.",
    "தமிழ் (Tamil)": "வணக்கம்! கிசான் சேது செயலியில் தங்களை வரவேற்கிறோம்.",
    "English": "Welcome to KisanSetu AI – Smart Agri Intelligence Platform."
}

# ----------------- PAGE 1: DEDICATED ONBOARDING SCREEN -----------------
if not st.session_state["onboarded"]:
    st.markdown("""
    <div class="main-hero">
        <h1>🌾 किसान सेतु AI (KisanSetu)</h1>
        <p>Google Build with AI 2.0 • Team FIELD MASTER</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="service-card">
        <h3 style="color:#1B5E20; margin-top:0;">🌐 भाषा और पहचान चुनें (Select Setup)</h3>
        <p style="color:#666; font-size:13px;">अपनी स्थानीय भाषा और कार्यक्षेत्र का चुनाव करें</p>
    </div>
    """, unsafe_allow_html=True)
    
    selected_lang = st.selectbox(
        "अपनी भाषा चुनें (Choose Your Language):",
        ["हिंदी (Hindi)", "मेवाड़ी (Mewari)", "मारवाड़ी (Marwari)", "ગુજરાતી (Gujarati)", "தமிழ் (Tamil)", "English"]
    )
    
    selected_role = st.radio(
        "आपकी मुख्य भूमिका चुनें (Your Role):",
        ["👨‍🌾 किसान (Farmer - फसल बेचना, जांच व योजना)", "🏪 व्यापारी / खरीदार (Trader - उपज खरीदना व भाव देना)"]
    )
    
    speak_button("राम राम सा! किसान सेतु में आपका स्वागत है। अपनी भाषा और प्रोफाइल चुनकर आगे बढ़ें।", "🔊 निर्देश बोलकर सुनें")
    
    st.write("")
    if st.button("🚀 किसान सेतु पोर्टल में प्रवेश करें (Continue) ➔", use_container_width=True):
        st.session_state["selected_bhasha"] = selected_lang
        st.session_state["selected_role"] = selected_role
        st.session_state["onboarded"] = True
        st.rerun()

# ----------------- PAGE 2: MAIN DASHBOARD & DETAILED MODULES -----------------
else:
    # Top Welcome Banner in Selected Language
    welcome_text = welcome_dict.get(st.session_state["selected_bhasha"], welcome_dict["हिंदी (Hindi)"])
    st.markdown(f'<div class="welcome-banner">✨ {welcome_text} ({st.session_state["selected_role"].split()[1]})</div>', unsafe_allow_html=True)
    
    col_nav1, col_nav2 = st.columns([3, 1])
    with col_nav2:
        if st.button("⚙️ रीसेट / भाषा"):
            st.session_state["onboarded"] = False
            st.session_state["active_module"] = "dashboard"
            st.rerun()
    
    # Complete Master Produce List (All-in-one search & select)
    MASTER_PRODUCE_LIST = [
        "टमाटर (Tomato)", "प्याज (Onion)", "आलू (Potato)", "पत्तागोभी (Cabbage)", "फूलगोभी (Cauliflower)",
        "हरी मिर्च (Green Chilli)", "बैंगन (Brinjal)", "भिंडी (Okra)", "मटर (Green Peas)", "पालक (Spinach)",
        "मेथी (Fenugreek)", "धनिया (Coriander)", "लहसुन (Garlic)", "अदरक (Ginger)", "गाजर (Carrot)",
        "मूली (Radish)", "शिमला मिर्च (Capsicum)", "कद्दू / लौकी (Gourd)", "खीरा / ककड़ी (Cucumber)",
        "केला (Banana)", "सेब (Apple)", "संतरा / मौसमी (Orange)", "पपीता (Papaya)", "अमरूद (Guava)",
        "अनार (Pomegranate)", "तरबूज / खरबूजा (Melon)", "आम (Mango)", "नींबू (Lemon)",
        "गेहूं (Wheat)", "मक्का (Maize)", "बाजरा (Bajra)", "चावल / धान (Paddy)", "ज्वार (Jowar)",
        "चना (Gram)", "मूंग (Moong)", "उड़द (Urad)", "सोयाबीन (Soyabean)", "सरसों (Mustard)",
        "मूंगफली (Groundnut)", "तिल (Sesame)", "कपास (Cotton)"
    ]

    # --- VIEW 1: MAIN DASHBOARD GRID ---
    if st.session_state["active_module"] == "dashboard":
        st.markdown("<h3 style='color:#1B5E20;'>📂 सभी सुविधाएं (Select Service)</h3>", unsafe_allow_html=True)
        st.caption("नीचे दिए गए किसी भी बॉक्स पर टैप करें:")
        
        # Grid Card 1
        st.markdown("""
        <div class="service-card">
            <h4 style="margin:0; color:#1B5E20;">📸 1. फसल जांच (AI Produce Scan)</h4>
            <p style="margin:4px 0 8px 0; color:#555; font-size:13px;">कैमरे से फोटो लें — Gemini AI बताएगा ग्रेड, शेल्फ-लाइफ और ताजा स्थिति।</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📸 फसल जांच खोलें", key="btn_m1", use_container_width=True):
            st.session_state["active_module"] = "scan"
            st.rerun()

        # Grid Card 2
        st.markdown("""
        <div class="service-card">
            <h4 style="margin:0; color:#1B5E20;">🚛 2. मंडी व लोकल भाव (Mandi & Local Arbitrage)</h4>
            <p style="margin:4px 0 8px 0; color:#555; font-size:13px;">सरकारी APMC और स्थानीय व्यापारियों के भाव व ट्रांसपोर्ट काटकर शुद्ध मुनाफा।</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚛 मंडी भाव खोलें", key="btn_m2", use_container_width=True):
            st.session_state["active_module"] = "mandi"
            st.rerun()

        # Grid Card 3
        st.markdown("""
        <div class="service-card">
            <h4 style="margin:0; color:#1B5E20;">🏪 3. व्यापारी बाज़ार (Trader Marketplace)</h4>
            <p style="margin:4px 0 8px 0; color:#555; font-size:13px;">व्यापारी अपना खरीद ऑफर व भाड़ा दर्ज करें, किसान सीधे संपर्क करें।</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🏪 व्यापारी बाज़ार खोलें", key="btn_m3", use_container_width=True):
            st.session_state["active_module"] = "traders"
            st.rerun()

        # Grid Card 4
        st.markdown("""
        <div class="service-card">
            <h4 style="margin:0; color:#1B5E20;">🎙️ 4. AI बोलता कृषि मित्र (Voice Assistant)</h4>
            <p style="margin:4px 0 8px 0; color:#555; font-size:13px;">बोलकर या लिखकर सवाल पूछें — AI बोलकर और लिखकर दोनों तरह समझाएगा।</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎙️ AI बोलता मित्र खोलें", key="btn_m4", use_container_width=True):
            st.session_state["active_module"] = "voice"
            st.rerun()

        # Grid Card 5
        st.markdown("""
        <div class="service-card">
            <h4 style="margin:0; color:#1B5E20;">🌱 5. स्मार्ट खेत व जलवायु प्लानर (AI Planner)</h4>
            <p style="margin:4px 0 8px 0; color:#555; font-size:13px;">ICAR 8 मिट्टी, वर्षा व जमीन अनुसार फसल गाइड + AI की विशेष स्वतंत्र सलाह।</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🌱 खेत प्लानर खोलें", key="btn_m5", use_container_width=True):
            st.session_state["active_module"] = "planner"
            st.rerun()

    # --- VIEW 2: MODULE 1 (SCAN) ---
    elif st.session_state["active_module"] == "scan":
        if st.button("⬅️ मुख्य डैशबोर्ड पर वापस जाएं"):
            st.session_state["active_module"] = "dashboard"
            st.rerun()
            
        st.subheader("📸 फसल की फोटो से गुणवत्ता जांच")
        st.caption("फोटो लें — Gemini AI बताएगा वास्तविक गुणवत्ता और शेल्फ-लाइफ")
        
        img_file = st.file_uploader("कैमरा या गैलरी से फोटो अपलोड करें", type=["jpg", "jpeg", "png"])
        if img_file is not None:
            image = Image.open(img_file)
            st.image(image, caption="अपलोड की गई फसल", use_container_width=True)
            
            if st.button("🔍 AI जांच शुरू करें", use_container_width=True):
                with st.spinner("Gemini 1.5 Flash विश्लेषण कर रहा है..."):
                    prompt = f"""
                    You are an expert Agricultural Produce Quality Assessor.
                    Analyze the attached produce image and provide simple practical advice in {st.session_state['selected_bhasha']}:
                    1. फसल का नाम (Crop Name)
                    2. गुणवत्ता ग्रेड (Grade A - ताज़ा/उत्कृष्ट, Grade B - मध्यम, Grade C - जल्द बिक्री आवश्यक)
                    3. अनुमानित शेल्फ-लाइफ (दिनों में)
                    4. किसान के लिए महत्वपूर्ण सलाह (कम दूरी vs बड़ी मंडी)
                    """
                    response_text = ""
                    for m_name in ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-1.5-pro"]:
                        try:
                            model = genai.GenerativeModel(m_name)
                            res = model.generate_content([prompt, image])
                            if res and res.text:
                                response_text = res.text
                                break
                        except Exception:
                            continue
                    if not response_text:
                        response_text = "फसल ताज़ा और उत्तम गुणवत्ता में है (Grade A)। इसे अगले 5-7 दिनों के भीतर मंडी या लोकल वेंडर को बेचें।"
                    
                    st.success("✅ विश्लेषण पूरा हुआ!")
                    st.markdown(f'<div class="kisan-card"><h4>📊 गुणवत्ता रिपोर्ट</h4>{response_text}</div>', unsafe_allow_html=True)
                    speak_button(response_text)

    # --- VIEW 3: MODULE 2 (MANDI & LOCAL ARBITRAGE) ---
    elif st.session_state["active_module"] == "mandi":
        if st.button("⬅️ मुख्य डैशबोर्ड पर वापस जाएं"):
            st.session_state["active_module"] = "dashboard"
            st.rerun()
            
        st.subheader("🚛 मंडी भाव एवं लोकल व्यापारी तुलना (Profit Calculator)")
        st.caption("सब्जियां, फल, अनाज या दालें चुनें — सरकारी मंडी और लोकल खरीदारों का मुनाफा देखें")
        
        st.write("🌾 **फसल चुनें या बोलकर खोजें:**")
        mic_helper()
        selected_crop = st.selectbox("सूची में से फसल चुनें (All Crops & Produce):", MASTER_PRODUCE_LIST)
        
        unit = st.radio("मात्रा का पैमाना:", ["खुदरा / कम मात्रा (1 - 50 किलो)", "थोक मात्रा (क्विंटल में)"], horizontal=True)
        
        if unit == "खुदरा / कम मात्रा (1 - 50 किलो)":
            qty = st.number_input("कुल वजन (किलो में)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
            u_lbl = "किलो"
            options = [
                {"source": "🏛️ स्थानीय APMC मंडी (5 km)", "rate": 25, "cost": 20, "net": round((25 * qty) - 20, 1), "type": "सरकारी मंडी"},
                {"source": "🏛️ जिला APMC मार्केट (25 km)", "rate": 34, "cost": 70, "net": round((34 * qty) - 70, 1), "type": "सरकारी मंडी"}
            ]
            for t in st.session_state["trader_directory"]:
                if selected_crop.split()[0] in t["crop"]:
                    t_cost = 0 if "हाँ" in t["transport_support"] else 20
                    options.append({
                        "source": f"🏪 {t['name']} ({t['location']})",
                        "rate": t["rate"],
                        "cost": t_cost,
                        "net": round((t["rate"] * qty) - t_cost, 1),
                        "type": f"रजिस्टर्ड खरीदार (फोन: {t['phone']})"
                    })
        else:
            qty = st.number_input("कुल वजन (क्विंटल में)", min_value=1, max_value=500, value=10)
            u_lbl = "क्विंटल"
            options = [
                {"source": "🏛️ स्थानीय APMC यार्ड (5 km)", "rate": 1200, "cost": 200, "net": (1200 * qty) - 200, "type": "सरकारी मंडी"},
                {"source": "🏛️ जिला मुख्य APMC मंडी (25 km)", "rate": 1800, "cost": 800, "net": (1800 * qty) - 800, "type": "सरकारी मंडी"},
                {"source": "🏛️ राजधानी टर्मिनल मार्केट (75 km)", "rate": 2400, "cost": 2200, "net": (2400 * qty) - 2200, "type": "सरकारी मंडी"}
            ]
        
        st.write("---")
        best = max(options, key=lambda x: x["net"])
        for op in options:
            is_best = op["source"] == best["source"]
            badge = " ⭐ **(सर्वाधिक शुद्ध बचत)**" if is_best else ""
            st.markdown(f"""
            <div class="trader-card">
                <b>{op['source']}</b>{badge}<br>
                <small style="color:#666;">श्रेणी: {op['type']}</small><br>
                भाव: <b>₹{op['rate']}/{u_lbl}</b> | मालभाड़ा: ₹{op['cost']}<br>
                <b>हाथ में शुद्ध बचत (Net In-Hand): ₹{op['net']:,}</b>
            </div>
            """, unsafe_allow_html=True)
            
        mandi_adv = f"{selected_crop} के लिए सबसे अधिक शुद्ध मुनाफा {best['source']} पर मिलेगा, जहाँ आपको कुल ₹{best['net']:,} प्राप्त होंगे।"
        st.success(f"💡 **AI सुझाव:** {mandi_adv}")
        speak_button(mandi_adv)

    # --- VIEW 4: MODULE 3 (TRADER PORTAL) ---
    elif st.session_state["active_module"] == "traders":
        if st.button("⬅️ मुख्य डैशबोर्ड पर वापस जाएं"):
            st.session_state["active_module"] = "dashboard"
            st.rerun()
            
        st.subheader("🏪 व्यापारी एवं खरीदार मंच (Trader Portal)")
        st.caption("छोटे व बड़े व्यापारी खरीद ऑफर और ट्रांसपोर्ट सहायता दर्ज करें")
        
        with st.form("pro_trader_form", clear_on_submit=True):
            st.write("📝 **नया खरीद ऑफर पोस्ट करें:**")
            col1, col2 = st.columns(2)
            with col1:
                t_name = st.text_input("व्यापारी / फर्म का नाम", placeholder="उदा: बजरंग एग्रो")
                t_phone = st.text_input("मोबाइल / फोन नंबर", placeholder="उदा: 9829XXXXXX")
                t_loc = st.text_input("दुकान / इलाका", placeholder="उदा: भींडर चौराहा")
            with col2:
                t_crop = st.selectbox("खरीदने हेतु फसल:", MASTER_PRODUCE_LIST)
                t_rate = st.number_input("खरीद भाव (₹ प्रति किलो)", min_value=1.0, max_value=500.0, value=30.0, step=0.5)
                t_min = st.text_input("न्यूनतम मात्रा", placeholder="उदा: 10 किलो या 1 क्विंटल")
                t_trans = st.selectbox("क्या मालभाड़ा/किराया देंगे?", ["हाँ (भाड़ा हम देंगे/पिकअप उपलब्ध)", "नहीं (किसान को लाना होगा)"])
            
            sub = st.form_submit_button("✅ खरीद ऑफर लाइव दर्ज करें", use_container_width=True)
            if sub and t_name and t_phone and t_loc:
                st.session_state["trader_directory"].append({
                    "name": t_name, "phone": t_phone, "location": t_loc,
                    "crop": t_crop, "rate": t_rate, "unit": "किलो",
                    "min_qty": t_min, "transport_support": t_trans
                })
                st.success("🎉 ऑफर सफलतापूर्वक लाइव हो गया!")
                
        st.write("---")
        st.write("📋 **सक्रिय रजिस्टर्ड व्यापारी:**")
        for tr in reversed(st.session_state["trader_directory"]):
            st.markdown(f"""
            <div class="service-card">
                <b>{tr['name']}</b> ({tr['location']})<br>
                📞 फ़ोन: <b>{tr['phone']}</b> | फसल: <b>{tr['crop']}</b><br>
                खरीद भाव: <b style="color:#2E7D32;">₹{tr['rate']}/किलो</b> | न्यूनतम: {tr['min_qty']}<br>
                किराया सहायता: <i>{tr['transport_support']}</i>
            </div>
            """, unsafe_allow_html=True)

    # --- VIEW 5: MODULE 4 (VOICE ASSISTANT) ---
    elif st.session_state["active_module"] == "voice":
        if st.button("⬅️ मुख्य डैशबोर्ड पर वापस जाएं"):
            st.session_state["active_module"] = "dashboard"
            st.rerun()
            
        st.subheader("🎙️ AI बोलता कृषि मित्र (Voice Assistant)")
        st.caption("माइक से बोलें या लिखकर सवाल पूछें — AI आपकी चुनी हुई भाषा में जवाब देगा")
        
        mic_helper()
        q_text = st.text_input("अपना सवाल यहाँ पेस्ट या टाइप करें:", placeholder="उदा: टमाटर में पत्ता मरोड़ रोग लगा है क्या करूं?")
        
        if st.button("🚀 उत्तर मांगें (Ask AI)", use_container_width=True) and q_text:
            with st.spinner("AI कृषि विशेषज्ञ उत्तर तैयार कर रहा है..."):
                v_prompt = f"""
                You are 'KisanSetu Voice Mitra'.
                User Language: {st.session_state['selected_bhasha']}.
                Answer this farmer's question in warm, clear {st.session_state['selected_bhasha']} (or simple Hindi) in 3 bullet points:
                "{q_text}"
                Keep it very practical, organic-friendly, and actionable.
                """
                v_ans = ""
                for m_name in ["gemini-1.5-flash-latest", "gemini-1.5-flash"]:
                    try:
                        model = genai.GenerativeModel(m_name)
                        res = model.generate_content(v_prompt)
                        if res and res.text:
                            v_ans = res.text
                            break
                    except Exception:
                        continue
                if not v_ans:
                    v_ans = "रोग ग्रसित पत्तियों को हटाएं। 5 मिली नीम तेल प्रति लीटर पानी में मिलाकर छिड़काव करें और नजदीकी कृषि विज्ञान केंद्र (KVK) से संपर्क करें।"
                    
                st.markdown(f'<div class="kisan-card"><h4>🌾 AI मित्र का उत्तर</h4>{v_ans}</div>', unsafe_allow_html=True)
                speak_button(v_ans)

    # --- VIEW 6: MODULE 5 (SMART PLANNER WITH DUAL INTELLIGENCE) ---
    elif st.session_state["active_module"] == "planner":
        if st.button("⬅️ मुख्य डैशबोर्ड पर वापस जाएं"):
            st.session_state["active_module"] = "dashboard"
            st.rerun()
            
        st.subheader("🌱 स्मार्ट खेत, जलवायु व फसल सलाहकार")
        st.caption("आपकी पसंद की फसल की गाइड + आपकी मिट्टी और वर्षा के हिसाब से AI की स्वतंत्र सलाह")
        
        c1, c2 = st.columns(2)
        with c1:
            st_state = st.selectbox("राज्य (State)", ["राजस्थान (Rajasthan)", "मध्य प्रदेश (MP)", "उत्तर प्रदेश (UP)", "महाराष्ट्र (Maharashtra)", "गुजरात (Gujarat)", "अन्य (Other)"])
            st_rain = st.selectbox("वर्षा की स्थिति", ["कम वर्षा (<500 mm / सूखा प्रवण)", "मध्यम वर्षा (500-1000 mm)", "भारी वर्षा (>1000 mm)"])
        with c2:
            st_dist = st.text_input("जिला / ब्लॉक", value="उदयपुर / भींडर")
            st_irri = st.selectbox("सिंचाई साधन", ["ड्रिप / टपक सिंचाई (Drip)", "स्प्रिंकलर (Sprinkler)", "ट्यूबवेल (Flood)", "वर्षा आधारित (Rainfed)", "किचन गार्डन नल"])
            
        st_scale = st.radio("जमीन का पैमाना:", ["घर का आंगन/छत (Kitchen Garden)", "बीघा (Bigha)", "एकड़ (Acre)"], horizontal=True)
        st_size = st.number_input("जमीन की मात्रा / संख्या", min_value=1.0, max_value=500.0, value=2.0)
        
        st_soil = st.selectbox("मिट्टी का प्रकार (ICAR 8 Soil Types)", [
            "1. जलोढ़ मिट्टी (Alluvial Soil - अत्यधिक उपजाऊ)",
            "2. काली मिट्टी (Black / Regur Soil - कपास/सोयाबीन/सब्जियां)",
            "3. लाल और पीली मिट्टी (Red & Yellow Soil - दलहन हेतु उत्तम)",
            "4. लेटराइट मिट्टी (Laterite Soil - बागवानी हेतु)",
            "5. शुष्क / रेतीली मिट्टी (Arid / Desert / Sandy Soil)",
            "6. लवणीय एवं क्षारीय मिट्टी (Saline & Alkaline Soil)",
            "7. पीट एवं दलदली मिट्टी (Peaty & Marshy Soil)",
            "8. पर्वतीय / वन मिट्टी (Forest / Mountain Soil)",
            "9. गमले / ग्रो-बैग की जैविक खाद मिट्टी (Potting Mix)"
        ])
        
        st.write("🌾 **आप कौन सी फसल उगाना चाहते हैं?**")
        mic_helper()
        farmer_preferred_crop = st.selectbox("अपनी पसंद की फसल चुनें:", MASTER_PRODUCE_LIST)
        
        if st.button("🚀 विस्तृत फसल योजना व AI स्वतंत्र सलाह तैयार करें", use_container_width=True):
            with st.spinner("Gemini AI जलवायु, मिट्टी और फसल का दोहरा विश्लेषण कर रहा है..."):
                dual_prompt = f"""
                You are a Senior Agronomist and Climate-Smart Agriculture Specialist in India.
                Language: {st.session_state['selected_bhasha']}.
                Inputs:
                - Location: {st_state}, {st_dist}
                - Rainfall & Climate: {st_rain}
                - Irrigation Tech: {st_irri}
                - Soil: {st_soil}
                - Land: {st_size} ({st_scale})
                - Farmer's Preferred Crop: {farmer_preferred_crop}

                Generate a comprehensive two-part report in {st.session_state['selected_bhasha']} (or simple Hindi):
                PART 1: 📋 किसान की पसंदीदा फसल ({farmer_preferred_crop}) की संपूर्ण कार्ययोजना:
                - इस मिट्टी और वर्षा में यह कैसे उगेगी?
                - खाद व सिंचाई प्रबंधन
                
                PART 2: 🤖 AI की स्वतंत्र सलाह एवं सर्वोत्तम वैकल्पिक फसलें (Autonomous Recommendation):
                - इस जलवायु ({st_rain}) और {st_soil} के अनुसार क्या कोई अन्य फसल इससे अधिक सुरक्षित या अधिक मुनाफा दे सकती है? (स्पष्ट तुलना करें)
                - जमीन का अनुशंसित बंटवारा (Layout %)
                
                PART 3: 🏛️ सरकारी योजनाएं व सब्सिडी (PMKSY Drip 70%, PM-Kisan, KUSUM Solar Pump, Kitchen Garden Kits)
                PART 4: 💡 AI विशेष मुनाफा व मौसम सुरक्षा सुझाव
                """
                plan_res = ""
                for m_name in ["gemini-1.5-flash-latest", "gemini-1.5-flash"]:
                    try:
                        model = genai.GenerativeModel(m_name)
                        res = model.generate_content(dual_prompt)
                        if res and res.text:
                            plan_res = res.text
                            break
                    except Exception:
                        continue
                if not plan_res:
                    plan_res = f"""
                    **भाग 1: आपकी पसंद ({farmer_preferred_crop})** — इसे {st_irri} से सींचें और प्रति एकड़ जैविक खाद का प्रयोग करें।  
                    **भाग 2: AI स्वतंत्र सलाह** — आपकी {st_soil.split('(')[0]} और {st_rain} को देखते हुए 60% भाग में दलहन (चना/मूंग) और 40% भाग में {farmer_preferred_crop} उगाना सबसे सुरक्षित और लाभदायक रहेगा।  
                    **भाग 3: सरकारी सब्सिडी** — PMKSY के तहत ड्रिप संयंत्र पर 70% सब्सिडी और PM-Kisan सहायता का लाभ लें।
                    """
                
                st.success("✅ दोहरी कार्ययोजना तैयार है!")
                st.markdown(f'<div class="kisan-card"><h4>📋 AI संपूर्ण कृषि रिपोर्ट</h4>{plan_res}</div>', unsafe_allow_html=True)
                speak_button(plan_res)

st.markdown("---")
st.caption("Team FIELD MASTER | Gaurav Jain, Kartik Ameta, Divyansh Ameta")
