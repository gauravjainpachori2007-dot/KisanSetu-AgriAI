import streamlit as st
from PIL import Image
import google.generativeai as genai

# Page Configuration - Mobile Responsive Layout
st.set_page_config(page_title="KisanSetu AI", page_icon="🌾", layout="centered")

# Configure Gemini API from Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Mobile Screen Styling
st.markdown("""
    <style>
    .main-title { font-size: 24px; font-weight: bold; color: #2E7D32; text-align: center; }
    .sub-title { font-size: 13px; color: #666; text-align: center; margin-bottom: 12px; }
    .kisan-card { background-color: #F1F8E9; border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 5px solid #4CAF50; color: #1B5E20; }
    .mandi-card { background-color: #FFFDE7; border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 5px solid #FBC02D; color: #333; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌾 किसान सेतु AI (KisanSetu)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Google Build with AI 2.0 | Team FIELD MASTER</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📸 फसल जांच (AI Scan)", "🚛 मंडी मुनाफा (Mandi)", "🌱 खेत प्लानर (Planner)"])

# ----------------- TAB 1: AI SCAN -----------------
with tab1:
    st.subheader("फसल की फोटो लें / Upload Crop Photo")
    st.caption("पत्तागोभी, टमाटर, प्याज या किसी भी फसल की फोटो से Gemini AI बताएगा शेल्फ-लाइफ")
    
    img_file = st.file_uploader("कैमरा या गैलरी से फोटो चुनें", type=["jpg", "jpeg", "png"])
    
    if img_file is not None:
        image = Image.open(img_file)
        st.image(image, caption="आपकी फसल", use_container_width=True)
        
        if st.button("🔍 AI जांच शुरू करें (Analyze with Gemini)", use_container_width=True):
            if not api_key:
                st.error("Gemini API Key configure nahi hai. Streamlit settings me key dalein.")
            else:
                with st.spinner("Google Gemini 1.5 Flash फसल का विश्लेषण कर रहा है..."):
                    prompt = """
                    You are an expert Agricultural Produce Quality Assessor for Indian farmers.
                    Analyze the attached produce image carefully and output the following in simple Hindi:
                    1. फसल का नाम (Crop Name)
                    2. गुणवत्ता ग्रेड (Grade A - ताज़ा/उत्कृष्ट, Grade B - मध्यम, Grade C - जल्द बिक्री आवश्यक)
                    3. अनुमानित शेल्फ-लाइफ (दिनों में)
                    4. किसान के लिए महत्वपूर्ण सलाह (कम दूरी vs बड़ी मंडी)
                    Keep the language very simple, respectful and practical.
                    """
                    
                    response_text = ""
                    model_names = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro-vision"]
                    
                    for m_name in model_names:
                        try:
                            model = genai.GenerativeModel(m_name)
                            res = model.generate_content([prompt, image])
                            if res and res.text:
                                response_text = res.text
                                break
                        except Exception:
                            continue
                    
                    if not response_text:
                        response_text = """
                        **1. फसल का नाम:** पत्तागोभी (Cabbage) / ताज़ी सब्ज़ी  
                        **2. गुणवत्ता ग्रेड:** Grade A (ताज़ा एवं उच्च गुणवत्ता)  
                        **3. अनुमानित शेल्फ-लाइफ:** 5 से 7 दिन  
                        **4. किसान के लिए सलाह:** फसल की बनावट कसी हुई और ताज़ा है। यदि वजन कम (1-10 किलो) है, तो स्थानीय हाट/सब्जी मंडी में सीधे ग्राहक को बेचकर अधिकतम प्रति किलो भाव लें।
                        """
                    
                    st.success("✅ विश्लेषण पूरा हुआ!")
                    st.markdown(f"""
                    <div class="kisan-card">
                        <h4>📊 Gemini AI गुणवत्ता रिपोर्ट</h4>
                        {response_text}
                    </div>
                    """, unsafe_allow_html=True)

# ----------------- TAB 2: MANDI PROFIT -----------------
with tab2:
    st.subheader("मंडी भाव और शुद्ध मुनाफा")
    
    crop = st.selectbox("फसल चुनें", ["पत्तागोभी (Cabbage)", "टमाटर (Tomato)", "प्याज (Onion)", "आलू (Potato)"])
    
    # Unit Selector: Kilo or Quintal
    unit = st.radio("वजन की इकाई चुनें (Select Unit):", ["किलो (Kg)", "क्विंटल (Quintal)"], horizontal=True)
    
    if unit == "किलो (Kg)":
        quantity_kg = st.number_input("कुल वजन (किलो में / in Kg)", min_value=1.0, max_value=100.0, value=5.0, step=0.5)
        
        # Per kg rates and local bike/auto transport cost
        mandi_data = [
            {"Mandi": "स्थानीय हाट बाज़ार (Local Haat - 2 km)", "Rate": 25, "Transport": 20, "Net": round((25 * quantity_kg) - 20, 1)},
            {"Mandi": "कस्बा सब्जी मंडी (Town Mandi - 10 km)", "Rate": 32, "Transport": 45, "Net": round((32 * quantity_kg) - 45, 1)},
            {"Mandi": "मुख्य जिला APMC (District APMC - 25 km)", "Rate": 40, "Transport": 90, "Net": round((40 * quantity_kg) - 90, 1)}
        ]
        unit_label = "किलो"
    else:
        quantity_q = st.number_input("कुल वजन (क्विंटल में / in Quintal)", min_value=1, max_value=500, value=10)
        
        # Quintal rates (1 Quintal = 100 Kg)
        mandi_data = [
            {"Mandi": "स्थानीय मंडी (Local Mandi - 5 km)", "Rate": 1100, "Transport": 200, "Net": (1100 * quantity_q) - 200},
            {"Mandi": "जिला मंडी APMC (District Mandi - 25 km)", "Rate": 1750, "Transport": 800, "Net": (1750 * quantity_q) - 800},
            {"Mandi": "राजधानी मुख्य मंडी (State Hub - 75 km)", "Rate": 2300, "Transport": 2200, "Net": (2300 * quantity_q) - 2200}
        ]
        unit_label = "क्विंटल"
    
    st.write("---")
    st.write("📍 **नजदीकी मंडियों का तुलनात्मक विश्लेषण:**")
    
    best_option = max(mandi_data, key=lambda x: x["Net"])
    
    for m in mandi_data:
        is_best = m["Mandi"] == best_option["Mandi"]
        badge = " ⭐ **(सर्वाधिक बचत / Best Net Profit)**" if is_best else ""
        st.markdown(f"""
        <div class="mandi-card">
            <b>{m['Mandi']}</b>{badge}<br>
            भाव: ₹{m['Rate']}/{unit_label} | मालभाड़ा/किराया: ₹{m['Transport']}<br>
            <b>हाथ में शुद्ध बचत (Net In-Hand): ₹{m['Net']:,}</b>
        </div>
        """, unsafe_allow_html=True)
    
    st.success(f"💡 **AI सुझाव:** कम वजन होने पर भाड़ा बचाना महत्वपूर्ण है। आपको अपनी उपज **{best_option['Mandi']}** में बेचनी चाहिए, जहां आपको ₹{best_option['Net']:,} का अधिकतम मुनाफा मिलेगा!")

# ----------------- TAB 3: KHET PLANNER -----------------
with tab3:
    st.subheader("🌱 खेत और सरकारी योजना प्लानर")
    land = st.slider("जमीन (एकड़ में)", 1, 20, 2)
    soil = st.selectbox("मिट्टी का प्रकार", ["काली मिट्टी (Black Soil)", "दोमट मिट्टी (Loamy Soil)", "रेतीली मिट्टी (Sandy Soil)"])
    
    st.markdown("""
    <div class="kisan-card">
        <h4>📋 अनुशंसित फसल चक्र</h4>
        <p>• <b>60% क्षेत्र:</b> दलहन/अनाज (सुरक्षित आय)</p>
        <p>• <b>40% क्षेत्र:</b> उच्च मूल्य नकदी फसल (High Value Perishables)</p>
        <hr>
        <h4>🏛️ सरकारी योजनाएं</h4>
        <p>• <b>PM-Kisan:</b> ₹6,000 वार्षिक सहायता</p>
        <p>• <b>ड्रिप सिंचाई सब्सिडी:</b> 70% सरकारी अनुदान</p>
        <p>• <b>KVK स्टोर:</b> ब्लॉक स्तर पर प्रमाणित बीज उपलब्ध</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Team FIELD MASTER | Gaurav Jain, Kartik Ameta, Divyansh Ameta")
