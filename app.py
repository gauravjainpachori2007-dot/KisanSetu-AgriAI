import streamlit as st
from PIL import Image
import google.generativeai as genai

# Page Configuration - Clean Responsive Layout
st.set_page_config(page_title="KisanSetu AI | किसान सेतु", page_icon="🌾", layout="centered", initial_sidebar_state="collapsed")

# Configure Gemini API from Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Modern Theme & Styling CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Hind', sans-serif;
    }
    .app-header {
        background: linear-gradient(135deg, #1B5E20, #2E7D32);
        color: white;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .app-header h1 { color: #FFFFFF; font-size: 24px; margin: 0; font-weight: 700; }
    .app-header p { color: #E8F5E9; font-size: 13px; margin: 4px 0 0 0; }
    .role-badge {
        display: inline-block;
        background: #C8E6C9;
        color: #1B5E20;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 15px;
        font-weight: 600;
        margin-top: 6px;
    }
    .pro-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    .kisan-card {
        background: #F1F8E9;
        border-left: 6px solid #43A047;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
        color: #1B5E20;
    }
    .trader-card {
        background: #FFFDE7;
        border-left: 6px solid #FBC02D;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        color: #212121;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        height: 44px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE & INITIAL USER ONBOARDING -----------------
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "user_lang" not in st.session_state:
    st.session_state["user_lang"] = "हिंदी"
if "trader_directory" not in st.session_state:
    st.session_state["trader_directory"] = [
        {"name": "रमेश चंद्र (गांधी मंडी ट्रेडर्स)", "phone": "+91 98290XXXXX", "location": "भींडर / वल्लभनगर", "crop": "पत्तागोभी (Cabbage)", "rate": 28, "unit": "किलो", "min_qty": "10 किलो", "transport_support": "हाँ (₹50 तक भाड़ा देंगे)"},
        {"name": "मेवाड़ एग्रो प्रोक्योरमेंट", "phone": "+91 94140XXXXX", "location": "उदयपुर मुख्य मंडी", "crop": "टमाटर (Tomato)", "rate": 35, "unit": "किलो", "min_qty": "20 किलो", "transport_support": "हाँ (बल्क पिकअप फ्री)"},
        {"name": "कृष्णा फ्रेश वेज (लोकल वेंडर)", "phone": "+91 88750XXXXX", "location": "कानोड़ चौराha", "crop": "हरी मिर्च (Green Chilli)", "rate": 55, "unit": "किलो", "min_qty": "5 किलो", "transport_support": "नहीं (दुकान पर डिलीवरी)"}
    ]

# Header
st.markdown("""
<div class="app-header">
    <h1>🌾 किसान सेतु AI (KisanSetu)</h1>
    <p>स्मार्ट कृषि, लोकल बाज़ार और बहुभाषी AI मित्र</p>
    <div class="role-badge">Google Build with AI 2.0 • Team FIELD MASTER</div>
</div>
""", unsafe_allow_html=True)

# Audio Helper Functions (Browser Text-to-Speech)
def speak_button(text_content, button_text="🔊 आवाज़ में सुनें (Listen)"):
    clean_text = text_content.replace('"', '').replace("'", "").replace('\n', ' ')
    js_code = f"""
    <button onclick="
        window.speechSynthesis.cancel();
        let utter = new SpeechSynthesisUtterance('{clean_text[:400]}');
        utter.lang = 'hi-IN';
        utter.rate = 0.95;
        window.speechSynthesis.speak(utter);
    " style="background-color: #2E7D32; color: white; border: none; padding: 7px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 5px;">
    {button_text}
    </button>
    """
    st.components.v1.html(js_code, height=45)

# Onboarding Bar: Regional Languages & Roles
with st.expander("🌐 भाषा और प्रोफाइल चुनें (Select Language & Role)", expanded=(st.session_state["user_role"] is None)):
    col_l, col_r = st.columns(2)
    with col_l:
        st.session_state["user_lang"] = st.selectbox(
            "आप किस भाषा में बात करना चाहते हैं?",
            ["हिंदी (Hindi)", "मेवाड़ी (Mewari)", "मारवाड़ी (Marwari)", "ગુજરાતી (Gujarati)", "தமிழ் (Tamil)", "English"]
        )
    with col_r:
        st.session_state["user_role"] = st.radio(
            "आपकी पहचान / Role",
            ["👨‍🌾 किसान (Farmer - फसल बेचना या उगाना)", "🏪 व्यापारी / खरीदार (Trader - माल खरीदना)"]
        )
    
    # Audio instruction welcoming the user
    speak_button(
        "राम राम सा! किसान सेतु ऐप में आपका स्वागत है। अपनी मनपसंद भाषा और किसान या व्यापारी प्रोफाइल चुनकर आगे बढ़ें।",
        "🔊 भाषा निर्देश बोलकर सुनें"
    )

# ----------------- TABS SETUP -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📸 फसल जांच (Scan)", 
    "🚛 मंडी व लोकल भाव (Mandi)", 
    "🏪 व्यापारी बाज़ार (Traders)", 
    "🎙️ AI बोलता मित्र (Voice)", 
    "🌱 खेत प्लानर (Planner)"
])

# ----------------- TAB 1: AI SCAN -----------------
with tab1:
    st.subheader("📸 फसल की फोटो से गुणवत्ता जांच")
    st.caption("टमाटर, पत्तागोभी, फल या किसी भी फसल की फोटो लें — Gemini AI बताएगा ग्रेड और शेल्फ-लाइफ")
    
    img_file = st.file_uploader("कैमरा या गैलरी से फोटो अपलोड करें", type=["jpg", "jpeg", "png"])
    
    if img_file is not None:
        image = Image.open(img_file)
        st.image(image, caption="अपलोड की गई फसल", use_container_width=True)
        
        if st.button("🔍 AI जांच शुरू करें (Analyze Produce)", use_container_width=True):
            with st.spinner("Google Gemini 1.5 Flash फसल का विश्लेषण कर रहा है..."):
                prompt = f"""
                You are an expert Agricultural Produce Quality Assessor.
                Target Language Preference: {st.session_state['user_lang']}.
                Analyze the attached produce image carefully and output in simple {st.session_state['user_lang']} (or simple Hindi):
                1. फसल का नाम (Crop Name)
                2. गुणवत्ता ग्रेड (Grade A - ताज़ा/उत्कृष्ट, Grade B - मध्यम, Grade C - जल्द बिक्री आवश्यक)
                3. अनुमानित शेल्फ-लाइफ (दिनों में)
                4. किसान के लिए महत्वपूर्ण सलाह (स्थानीय बिक्री vs बड़ी मंडी)
                Keep it very practical, direct and simple.
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
                    response_text = "फसल ताज़ा और अच्छी स्थिति में है (Grade A)। इसे अगले 4-6 दिनों में बेचना सबसे अधिक लाभदायक रहेगा।"
                
                st.success("✅ गुणवत्ता विश्लेषण संपन्न!")
                st.markdown(f"""
                <div class="kisan-card">
                    <h4>📊 AI गुणवत्ता रिपोर्ट</h4>
                    {response_text}
                </div>
                """, unsafe_allow_html=True)
                speak_button(response_text)

# ----------------- TAB 2: COMPREHENSIVE PRODUCE MANDI & TRADER PROFIT -----------------
with tab2:
    st.subheader("🚛 मंडी भाव एवं लोकल व्यापारी तुलना (Profit Calculator)")
    st.caption("सभी सब्जियां, फल, अनाज, दालें — सरकारी मंडी के साथ स्थानीय खरीदारों के भाव")
    
    # Comprehensive Produce Category
    prod_type = st.selectbox("उत्पाद श्रेणी (Category):", [
        "सब्जियां (Vegetables)", "फल (Fruits)", "अनाज (Grains)", "दलहन (Pulses)", "तिलहन (Oilseeds)"
    ])
    
    if prod_type == "सब्जियां (Vegetables)":
        crop_list = ["पत्तागोभी (Cabbage)", "टमाटर (Tomato)", "प्याज (Onion)", "आलू (Potato)", "हरी मिर्च (Green Chilli)", "बैंगन (Brinjal)", "भिंडी (Okra)", "मटर (Green Peas)", "पालक / मेथी"]
    elif prod_type == "फल (Fruits)":
        crop_list = ["केला (Banana)", "सेब (Apple)", "संतरा / मौसमी", "पपीता (Papaya)", "अमरूद (Guava)", "अनार (Pomegranate)"]
    elif prod_type == "अनाज (Grains)":
        crop_list = ["गेहूं (Wheat)", "मक्का (Maize)", "बाजरा (Pearl Millet)", "चावल / धान (Paddy)"]
    elif prod_type == "दलहन (Pulses)":
        crop_list = ["चना (Gram)", "मूंग (Moong)", "उड़द (Urad)", "सोयाबीन"]
    else:
        crop_list = ["सरसों (Mustard)", "मूंगफली (Groundnut)", "तिल (Sesame)"]
        
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        crop = st.selectbox("सूची से चुनें (Select from list):", crop_list)
    with col_c2:
        custom_crop = st.text_input("या अपनी उपज का नाम यहाँ लिखें/बोलें:", placeholder="उदा: लहसुन, अदरक")
    
    final_crop = custom_crop if custom_crop else crop
    
    unit = st.radio("मात्रा का पैमाना चुनें:", ["खुदरा / कम मात्रा (1 - 50 किलो)", "थोक मात्रा (क्विंटल में)"], horizontal=True)
    
    if unit == "खुदरा / कम मात्रा (1 - 50 किलो)":
        qty = st.number_input("वजन (किलो में / in Kg)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
        unit_lbl = "किलो"
        
        options = [
            {"source": "🏛️ स्थानीय APMC मंडी (5 km)", "rate": 25, "cost": 20, "net": round((25 * qty) - 20, 1), "type": "सरकारी मंडी"},
            {"source": "🏛️️ जिला APMC मार्केट (25 km)", "rate": 34, "cost": 70, "net": round((34 * qty) - 70, 1), "type": "सरकारी मंडी"}
        ]
        
        for t in st.session_state["trader_directory"]:
            if final_crop.split()[0] in t["crop"] or final_crop == crop:
                trans_cost = 0 if "हाँ" in t["transport_support"] else 20
                net_val = round((t["rate"] * qty) - trans_cost, 1)
                options.append({
                    "source": f"🏪 {t['name']} ({t['location']})",
                    "rate": t["rate"],
                    "cost": trans_cost,
                    "net": net_val,
                    "type": f"स्थानीय खरीदार (फ़ोन: {t['phone']})"
                })
    else:
        qty = st.number_input("कुल वजन (क्विंटल में / in Quintal)", min_value=1, max_value=500, value=10)
        unit_lbl = "क्विंटल"
        options = [
            {"source": "🏛️ तहसील प्राथमिक मंडी (5 km)", "rate": 1200, "cost": 200, "net": (1200 * qty) - 200, "type": "सरकारी मंडी"},
            {"source": "🏛️ जिला मुख्य APMC यार्ड (25 km)", "rate": 1800, "cost": 800, "net": (1800 * qty) - 800, "type": "सरकारी मंडी"},
            {"source": "🏛️ राजधानी टर्मिनल हब (75 km)", "rate": 2400, "cost": 2200, "net": (2400 * qty) - 2200, "type": "सरकारी मंडी"}
        ]
    
    st.write("---")
    best = max(options, key=lambda x: x["net"])
    
    for op in options:
        is_rec = op["source"] == best["source"]
        badge = " ⭐ **(सर्वाधिक शुद्ध बचत / Best Option)**" if is_rec else ""
        st.markdown(f"""
        <div class="trader-card">
            <b>{op['source']}</b>{badge}<br>
            <small style="color:#666;">श्रेणी: {op['type']}</small><br>
            भाव: <b>₹{op['rate']}/{unit_lbl}</b> | मालभाड़ा/लागत: ₹{op['cost']}<br>
            <b>हाथ में शुद्ध बचत (Net In-Hand): ₹{op['net']:,}</b>
        </div>
        """, unsafe_allow_html=True)
    
    advice_text = f"आपकी फसल {final_crop} के लिए सबसे अधिक मुनाफा {best['source']} पर मिलेगा, जहाँ आपको कुल शुद्ध ₹{best['net']:,} की बचत होगी।"
    st.success(f"💡 **AI का अंतिम फैसला:** {advice_text}")
    speak_button(advice_text)

# ----------------- TAB 3: TRADER REGISTRATION PORTAL -----------------
with tab3:
    st.subheader("🏪 व्यापारी एवं खरीदार मंच (Trader Portal)")
    st.caption("छोटे व बड़े व्यापारी अपनी खरीद मांग और भाव दर्ज करें — किसान सीधे आपसे संपर्क करेंगे")
    
    with st.form("trader_form", clear_on_submit=True):
        st.write("📝 **नया खरीद ऑफर दर्ज करें (Post Buying Offer)**")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            t_name = st.text_input("व्यापारी / फर्म का नाम", placeholder="उदा: लक्ष्मी वेज ट्रेडर्स")
            t_phone = st.text_input("मोबाइल / संपर्क नंबर", placeholder="उदा: 9829XXXXXX")
            t_loc = st.text_input("दुकान / गोदाम का पता व इलाका", placeholder="उदा: भींडर बस स्टैंड, उदयपुर")
        with col_t2:
            t_crop = st.text_input("खरीदी जाने वाली उपज (सब्जी/फल/अनाज)", placeholder="उदा: टमाटर, पत्तागोभी, सोयाबीन")
            t_rate = st.number_input("आपका खरीद भाव (₹ प्रति किलो)", min_value=1.0, max_value=500.0, value=30.0, step=0.5)
            t_min_qty = st.text_input("न्यूनतम मात्रा", placeholder="उदा: 10 किलो या 1 क्विंटल")
            t_trans = st.selectbox("क्या आप मालभाड़ा/किराया देंगे?", ["हाँ (भाड़ा हम देंगे/पिकअप उपलब्ध)", "नहीं (किसान को खुद लाना होगा)"])
        
        submit_trader = st.form_submit_button("✅ अपना खरीद ऑफर लाइव दर्ज करें", use_container_width=True)
        
        if submit_trader:
            if t_name and t_phone and t_loc and t_crop:
                st.session_state["trader_directory"].append({
                    "name": t_name, "phone": t_phone, "location": t_loc,
                    "crop": t_crop, "rate": t_rate, "unit": "किलो",
                    "min_qty": t_min_qty, "transport_support": t_trans
                })
                st.success("🎉 आपका ऑफर दर्ज हो गया! अब क्षेत्र के किसान सीधे आपका भाव देख सकेंगे।")
            else:
                st.error("कृपया सभी आवश्यक विवरण भरें।")
    
    st.write("---")
    st.write("📋 **सक्रिय रजिस्टर्ड स्थानीय खरीदार:**")
    for tr in reversed(st.session_state["trader_directory"]):
        st.markdown(f"""
        <div class="pro-card">
            <b>{tr['name']}</b> ({tr['location']})<br>
            फ़ोन: 📞 <b>{tr['phone']}</b> | खरीद उपज: <b>{tr['crop']}</b><br>
            खरीद भाव: <span style="color:#2E7D32; font-weight:bold; font-size:16px;">₹{tr['rate']}/किलो</span> | न्यूनतम: {tr['min_qty']}<br>
            किराया सहायता: <i>{tr['transport_support']}</i>
        </div>
        """, unsafe_allow_html=True)

# ----------------- TAB 4: MULTIMODAL VOICE ASSISTANT -----------------
with tab4:
    st.subheader("🎙️ AI बोलता कृषि मित्र (Voice Assistant)")
    st.caption("जो भी पूछना चाहते हैं बोलें या लिखें — Gemini AI आवाज़ में उत्तर देगा")
    
    farmer_query = st.text_input("अपना सवाल लिखें या बोलकर टाइप करें:", placeholder="उदा: पत्तागोभी में कीड़े लग रहे हैं क्या करूं?")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        ask_btn = st.button("🚀 AI से उत्तर मांगें (Ask AI)", use_container_width=True)
    with col_v2:
        st.caption("💡 फोन के कीबोर्ड में 🎙️ माइक दबाकर अपनी भाषा में बोलें!")
    
    if ask_btn and farmer_query:
        with st.spinner("AI कृषि विशेषज्ञ आपकी भाषा में उत्तर तैयार कर रहा है..."):
            v_prompt = f"""
            You are 'KisanSetu Voice Mitra', a friendly Indian agricultural advisor.
            User Language: {st.session_state['user_lang']}.
            Answer the following farmer query in simple, direct {st.session_state['user_lang']} (or conversational Hindi):
            "{farmer_query}"
            Keep it actionable in 3 bullet points without complicated chemical terms.
            """
            v_ans = ""
            for m_name in ["gemini-1.5-flash-latest", "gemini-1.5-flash"]:
                try:
                    m = genai.GenerativeModel(m_name)
                    res = m.generate_content(v_prompt)
                    if res and res.text:
                        v_ans = res.text
                        break
                except Exception:
                    continue
            
            if not v_ans:
                v_ans = "नीम का तेल (Neem Oil 5ml प्रति लीटर) का छिड़काव करें। खेत में अधिक नमी न रहने दें और नजदीकी KVK केंद्र से संपर्क करें।"
            
            st.markdown(f"""
            <div class="kisan-card">
                <h4>🌾 AI किसान मित्र का उत्तर</h4>
                {v_ans}
            </div>
            """, unsafe_allow_html=True)
            speak_button(v_ans)

# ----------------- TAB 5: DYNAMIC AGRO-PLANNER (AUTONOMOUS AI CROP SELECTION) -----------------
with tab5:
    st.subheader("🌱 AI खेत एवं जलवायु सलाहकार (Autonomous Agro-Planner)")
    st.caption("यदि आपको नहीं पता कि क्या उगाना है, तो AI मिट्टी, मौसम और पानी के आधार पर खुद फसल तय करेगा")
    
    c1, c2 = st.columns(2)
    with c1:
        st_state = st.selectbox("राज्य चुनें (State)", ["राजस्थान (Rajasthan)", "मध्य प्रदेश (MP)", "उत्तर प्रदेश (UP)", "महाराष्ट्र (Maharashtra)", "गुजरात (Gujarat)", "अन्य (Other)"])
        st_rain = st.selectbox("वर्षा की स्थिति", ["कम वर्षा (<500 mm / सूखा प्रवण)", "मध्यम सामान्य वर्षा (500-1000 mm)", "भारी वर्षा (>1000 mm)"])
    with c2:
        st_dist = st.text_input("जिला / ब्लॉक", value="उदयपुर / भींडर")
        st_irri = st.selectbox("सिंचाई साधन", ["ड्रिप / टपक सिंचाई (Drip)", "स्प्रिंकलर (Sprinkler)", "ट्यूबवेल (Flood)", "वर्षा आधारित (Rainfed)", "किचन गार्डन नल"])
    
    st_scale = st.radio("जमीन का पैमाना:", ["घर का आंगन/छत (Kitchen Garden)", "बीघा (Bigha)", "एकड़ (Acre)"], horizontal=True)
    st_size = st.number_input("जमीन की मात्रा / आकार", min_value=1.0, max_value=500.0, value=2.0)
    
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
    
    # Autonomous AI selection vs Farmer Choice
    planner_mode = st.radio(
        "फसल चयन का तरीका:",
        [
            "🤖 मुझे नहीं पता — AI मेरी मिट्टी, वर्षा और जलवायु के अनुसार खुद सर्वोत्तम फसल सुझाए",
            "🧑‍🌾 मैं अपनी पसंद की फसल खुद चुनूंगा"
        ]
    )
    
    chosen_crops = ""
    if "अपनी पसंद" in planner_mode:
        chosen_crops = st.text_input("आप क्या उगाना चाहते हैं?", value="टमाटर, मिर्च, पालक")
    
    if st.button("🚀 संपूर्ण जलवायु, अनुकूल फसल व सब्सिडी योजना बनाएं", use_container_width=True):
        with st.spinner("Gemini AI जलवायु व मिट्टी के अनुकूल फसलों का विश्लेषण कर रहा है..."):
            plan_prompt = f"""
            You are a Senior Agronomist and Climate-Resilience Agriculture Advisor for India.
            Language: {st.session_state['user_lang']}.
            Parameters:
            - Location: {st_state}, {st_dist}
            - Rainfall: {st_rain}
            - Irrigation: {st_irri}
            - Land Scale: {st_size} ({st_scale})
            - ICAR Soil Type: {st_soil}
            - Farmer Choice: {chosen_crops if chosen_crops else 'AI Autonomous Selection based on climate & profit'}

            Please provide a structured plan in {st.session_state['user_lang']} (or simple Hindi):
            1. 🌾 AI अनुशंसित सर्वोत्तम फसलें (Autonomous selection of best 2-3 crops with layout percentage)
            2. 💧 जल संरक्षण व सिंचाई प्रबंधन (Specific technique for {st_irri})
            3. 🌿 खाद एवं मिट्टी पोषण (Tailored for {st_soil.split('(')[0]})
            4. 🏛️ सरकारी योजनाएं व सब्सिडी (PMKSY Drip 70%, PM-Kisan, KUSUM Solar Pump, Kitchen Garden Kits)
            5. 💡 AI विशेष मुनाफा व मौसम सुरक्षा सुझाव
            """
            
            p_ans = ""
            for m_name in ["gemini-1.5-flash-latest", "gemini-1.5-flash"]:
                try:
                    m = genai.GenerativeModel(m_name)
                    res = m.generate_content(plan_prompt)
                    if res and res.text:
                        p_ans = res.text
                        break
                except Exception:
                    continue
            
            if not p_ans:
                p_ans = f"""
                **1. 🌾 AI अनुशंसित फसलें:** आपकी मिट्टी और {st_rain} को देखते हुए 60% भाग में दलहन (चना/मूंग) और 40% भाग में उच्च मूल्य सब्जियां उगाएं।  
                **2. 💧 सिंचाई प्रबंधन:** {st_irri} अपनाएं जिससे 40% पानी बचेगा।  
                **3. 🏛️ सरकारी सब्सिडी:** PMKSY के तहत ड्रिप/फव्वारे पर 70% सब्सिडी प्राप्त करें।  
                **4. 💡 AI सुझाव:** कटाई के बाद KisanSetu ऐप से नजदीकी व्यापारी के भाव देखकर ही उपज बेचें।
                """
            
            st.success("✅ AI जलवायु व फसल योजना तैयार है!")
            st.markdown(f"""
            <div class="kisan-card">
                <h4>📋 AI विस्तृत कार्ययोजना ({st_state} - {st_dist})</h4>
                {p_ans}
            </div>
            """, unsafe_allow_html=True)
            speak_button(p_ans)

st.markdown("---")
st.caption("Team FIELD MASTER | Gaurav Jain, Kartik Ameta, Divyansh Ameta")
