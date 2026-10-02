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
    .kisan-card { background-color: #F1F8E9; border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 5px solid #4CAF50; }
    .mandi-card { background-color: #FFFDE7; border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 5px solid #FBC02D; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌾 किसान सेतु AI (KisanSetu)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Google Build with AI 2.0 | Team FIELD MASTER</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📸 फसल जांच (AI Scan)", "🚛 मंडी मुनाफा (Mandi)", "🌱 खेत प्लानर (Planner)"])

# ----------------- TAB 1: AI SCAN -----------------
with tab1:
    st.subheader("फसल की फोटो लें / Upload Crop Photo")
    st.caption("टमाटर, प्याज या किसी भी फसल की फोटो से Gemini AI बताएगा शेल्फ-लाइफ")
    
    img_file = st.file_uploader("कैमरा या गैलरी से फोटो चुनें", type=["jpg", "jpeg", "png"])
    
    if img_file is not None:
        image = Image.open(img_file)
        st.image(image, caption="आपकी फसल", use_column_width=True)
        
        if st.button("🔍 AI जांच शुरू करें (Analyze with Gemini)", use_container_width=True):
            if not api_key:
                st.error("Gemini API Key configure nahi hai. Streamlit settings me key dalein.")
            else:
                with st.spinner("Google Gemini 1.5 Flash फसल का विश्लेषण कर रहा है..."):
                    try:
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = """
                        You are an expert Agricultural Produce Quality Assessor for Indian farmers.
                        Analyze the attached produce image carefully and output the following in simple Hindi:
                        1. Fasal ka naam (Crop Name)
                        2. Quality Grade (Grade A - Fresh/Premium, Grade B - Good, Grade C - Perishable/Needs Quick Sale)
                        3. Estimated Remaining Shelf-Life (in days)
                        4. Actionable Advice for Farmer (Kisan ke liye sujhav)
                        Keep the language very simple and encouraging.
                        """
                        response = model.generate_content([prompt, image])
                        
                        st.success("✅ विश्लेषण पूरा हुआ!")
                        st.markdown(f"""
                        <div class="kisan-card">
                            <h4>📊 Gemini AI गुणवत्ता रिपोर्ट</h4>
                            {response.text}
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error analyzing image: {e}")

# ----------------- TAB 2: MANDI PROFIT -----------------
with tab2:
    st.subheader("मंडी भाव और शुद्ध मुनाफा")
    crop = st.selectbox("फसल चुनें", ["टमाटर (Tomato)", "प्याज (Onion)", "आलू (Potato)"])
    quantity = st.number_input("कुल वजन (क्विंटल में)", min_value=1, max_value=500, value=10)
    
    st.write("---")
    st.write("📍 **नजदीकी मंडियों का तुलनात्मक विश्लेषण:**")
    
    mandi_data = [
        {"Mandi": "स्थानीय मंडी (5 km)", "Rate": 1200, "Transport": 200, "Net": (1200 * quantity) - 200},
        {"Mandi": "जिला मंडी APMC (25 km)", "Rate": 1850, "Transport": 800, "Net": (1850 * quantity) - 800},
        {"Mandi": "राजधानी मंडी (75 km)", "Rate": 2400, "Transport": 2200, "Net": (2400 * quantity) - 2200}
    ]
    
    best_option = max(mandi_data, key=lambda x: x["Net"])
    
    for m in mandi_data:
        is_best = m["Mandi"] == best_option["Mandi"]
        badge = " ⭐ **(सर्वाधिक लाभ)**" if is_best else ""
        st.markdown(f"""
        <div class="mandi-card">
            <b>{m['Mandi']}</b>{badge}<br>
            भाव: ₹{m['Rate']}/क्विंटल | मालभाड़ा: ₹{m['Transport']}<br>
            <b>शुद्ध बचत (Net In-Hand): ₹{m['Net']:,}</b>
        </div>
        """, unsafe_allow_html=True)
    
    st.success(f"💡 **AI सुझाव:** आपको अपनी फसल **{best_option['Mandi']}** ले जानी चाहिए, जहां आपको ₹{best_option['Net']:,} का अधिकतम मुनाफा मिलेगा!")

# ----------------- TAB 3: KHET PLANNER -----------------
with tab3:
    st.subheader("🌱 खेत और सरकारी योजना प्लानर")
    land = st.slider("जमीन (एकड़ में)", 1, 20, 2)
    soil = st.selectbox("मिट्टी का प्रकार", ["काली मिट्टी (Black Soil)", "दोमट मिट्टी (Loamy Soil)", "रेतीली मिट्टी (Sandy Soil)"])
    
    st.markdown("""
    <div class="kisan-card">
        <h4>📋 अनुशंसित फसल चक्र</h4>
        <p>• <b>60% क्षेत्र:</b> दलहन/अनाज (कम पानी, सुरक्षित आय)</p>
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
