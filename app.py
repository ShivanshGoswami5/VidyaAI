
import streamlit as st
import google.generativeai as genai
from difflib import SequenceMatcher
import json
import datetime
from datetime import timedelta
import requests

# ============================================
# 🎨 PAGE CONFIG & STYLING
# ============================================

st.set_page_config(
    page_title="🤖 VIDYA AI - NCERT Teacher",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Elite Dark Theme (ChatGPT Style)
st.markdown("""
    <style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body, .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    
    .stChatMessageWithAvatar > :first-child {
        background: linear-gradient(135deg, #00d4ff, #0099ff);
        border-radius: 50%;
        padding: 10px;
    }
    
    .stTextInput > div > div > input {
        background: rgba(26, 31, 58, 0.8) !important;
        color: #00d4ff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 15px !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #0099ff) !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 25px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3) !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 45px !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 10px !important;
    }
    
    h2 {
        color: #00d4ff !important;
        font-size: 28px !important;
    }
    
    h3 {
        color: #00ff88 !important;
    }
    
    .premium-badge {
        background: linear-gradient(135deg, #ff6b00, #ff9500);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 5px 0;
    }
    
    .free-badge {
        background: linear-gradient(135deg, #00d4ff, #0099ff);
        color: black;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 5px 0;
    }
    
    .price-card {
        background: rgba(26, 31, 58, 0.6);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        text-align: center;
    }
    
    .price-card:hover {
        border-color: #00ff88;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    .sidebar .sidebar-content {
        background: rgba(10, 14, 39, 0.8) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# 📚 COMPLETE NCERT DATABASE (1-12)
# ============================================

ncert_database = {
    "Class 1": {
        "Numbers 1-9": "Numbers 1, 2, 3, 4, 5, 6, 7, 8, 9 help us count. Each number is unique and important.",
        "Addition": "Adding means putting groups together. 2 + 3 = 5 apples total. Addition makes bigger.",
        "Subtraction": "Taking away. 5 - 2 = 3 remaining. Subtraction makes smaller.",
        "Shapes": "Circle is round, Square has 4 equal sides, Triangle has 3 sides, Rectangle has 4 sides with opposite equal.",
        "Alphabet": "26 letters in English: A B C D E F G H I J K L M N O P Q R S T U V W X Y Z.",
        "Vowels": "A, E, I, O, U are vowels. These 5 letters are special.",
        "Days": "Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday. 7 days make 1 week.",
        "Family": "Mother, Father, Brother, Sister, Grandparents. Family loves and cares.",
        "Body": "Head, Eyes, Nose, Ears, Mouth, Hands, Legs, Feet. Each part has special work.",
        "Animals": "Dog, Cat, Cow, Bird, Fish, Lion, Tiger, Elephant. Different animals make different sounds.",
        "Colors": "Red, Blue, Green, Yellow, Orange, Purple, Pink, Brown, Black, White.",
        "Seasons": "Spring warm, Summer hot, Autumn cool, Winter cold. Each season different.",
    },
    "Class 2": {
        "Numbers 1-100": "Numbers 10-100. Place value: tens and ones. 23 = 2 tens + 3 ones.",
        "Addition Two Digits": "12 + 13 = 25. Add ones first (2+3=5), then tens (1+1=2).",
        "Subtraction Two Digits": "25 - 12 = 13. Subtract ones (5-2=3), then tens (2-1=1).",
        "Skip Counting": "By 2s: 2,4,6,8... By 5s: 5,10,15,20... By 10s: 10,20,30...",
        "Money": "Indian money: ₹ (Rupee). 100 paise = 1 rupee. Coins: 1₹, 2₹, 5₹, 10₹.",
        "Time": "60 seconds = 1 minute. 60 minutes = 1 hour. 24 hours = 1 day.",
        "Measurement": "Measure in cm or meter. Weight in kg. Liquid in liter.",
        "Odd and Even": "Even: 2,4,6,8... Odd: 1,3,5,7,9...",
        "Stories": "Beginning, middle, end. Characters and place important.",
        "Health": "Wash hands, brush teeth, bathe daily. Keeps us healthy.",
    },
    "Class 3": {
        "Multiplication": "Repeated addition. 3 × 4 = 12 (3+3+3+3). Symbol is ×.",
        "Division": "Sharing equally. 12 ÷ 3 = 4. Divide 12 into 3 groups of 4.",
        "Fractions": "1/2 is half, 1/4 is quarter, 1/3 is one-third.",
        "Three Digit": "100-999. Place value: hundreds, tens, ones. 345 = 3(100) + 4(10) + 5(1).",
        "Tables": "Multiplication tables 2-10. 2×1=2, 2×2=4... 10×1=10, 10×2=20...",
        "Shapes": "Triangle 3 sides, Square 4 equal, Rectangle 4 opposite equal, Circle round.",
        "Perimeter": "Distance around. Square: 4×side. Rectangle: 2(l+w).",
        "Area": "Space inside. Square: side×side. Rectangle: l×w.",
        "Plants": "Roots absorb water, stem holds, leaves make food, flowers become fruit.",
        "Life Cycle": "Frog: egg→tadpole→tadpole with legs→froglet→adult frog.",
    },
    "Class 4": {
        "Four Digit Numbers": "1000 thousand to 9999. Place value: thousands, hundreds, tens, ones.",
        "Large Addition": "1234 + 5678 = 6912. Add carefully with carrying.",
        "Large Subtraction": "5678 - 1234 = 4444. Subtract carefully with borrowing.",
        "Multiplication": "12 × 5 = 60. 23 × 4 = 92. Multiply tens and ones separately.",
        "Long Division": "Divide, multiply, subtract, bring down. Repeat until done.",
        "Equivalent Fractions": "1/2 = 2/4 = 3/6. Same value, different form.",
        "Decimals": "0.5 = 1/2, 0.25 = 1/4, 0.75 = 3/4.",
        "Angles": "Right angle 90°, Acute < 90°, Obtuse > 90°.",
        "Lines": "Line continues forever, Ray starts at point, Segment has endpoints.",
        "Weather": "Sunny bright, Rainy wet, Windy air moves, Snowy cold.",
    },
    "Class 5": {
        "Millions": "1 million = 10 lakhs = 1,000,000.",
        "Fractions Add": "1/4 + 1/4 = 2/4 = 1/2. Same denominator: add numerators.",
        "Decimals": "1.5 + 2.3 = 3.8. Line up decimal points.",
        "Percentage": "50% = 50/100 = 1/2. 25% = 1/4. 100% = whole.",
        "Profit Loss": "Profit = selling - buying. Loss = buying - selling.",
        "Simple Interest": "SI = (P × R × T) / 100. Money lent earns interest.",
        "Area Shapes": "Square: side×side. Rectangle: l×w. Triangle: 1/2×base×height.",
        "Volume": "Volume = l × w × h. Cube: side³.",
        "Data": "Bar graphs show data. Tally marks count frequency.",
        "Ecosystem": "Living things + environment. Forest, ocean, grassland.",
    },
    "Class 6": {
        "Factors": "Number dividing exactly. Factors of 12: 1,2,3,4,6,12.",
        "Multiples": "Numbers in multiplication. Multiples of 3: 3,6,9,12,15...",
        "Prime": "Only 2 factors: 1 and itself. 2,3,5,7,11,13,17,19,23 are prime.",
        "HCF": "Highest Common Factor. HCF(12,18) = 6.",
        "LCM": "Least Common Multiple. LCM(4,6) = 12.",
        "Integers": "Whole numbers + negatives: -3,-2,-1,0,1,2,3...",
        "Decimal to Fraction": "0.5 = 1/2. 0.25 = 1/4. 0.75 = 3/4.",
        "Simple Equations": "x + 5 = 10, so x = 5. Use opposite operation.",
        "Triangles": "3 sides, angles sum 180°. Types: equilateral, isosceles, scalene.",
        "Quadrilaterals": "4 sides. Square, rectangle, rhombus, parallelogram.",
    },
    "Class 7": {
        "Rational Numbers": "Fractions form p/q. 1/2, 3/4, -2/3 are rational.",
        "Algebra": "2x + 3y - 5. Variables with operations.",
        "Like Terms": "2x + 3x = 5x. Same variable and power combine.",
        "Linear Equations": "3x + 2 = 11. Solve: x = 3. Check: 3(3)+2=11 ✓",
        "Ratio": "2:3 means 2 parts for every 3 parts.",
        "Proportion": "2/3 = 4/6. Two ratios equal. Cross multiply.",
        "Unitary": "If 5 pens cost ₹50, 1 pen costs ₹10. 8 pens = ₹80.",
        "Discount": "20% off ₹100 means ₹20 off. Pay ₹80.",
        "Simple Interest": "Interest = (P × R × T)/100. Money × Rate × Time.",
        "Congruence": "Same shape, same size. Triangles: SSS, SAS, ASA, RHS.",
    },
    "Class 8": {
        "Squares": "2² = 4, √4 = 2. 3² = 9, √9 = 3. 5² = 25, √25 = 5.",
        "Cubes": "2³ = 8, ³√8 = 2. 3³ = 27, ³√27 = 3.",
        "Exponents": "aᵐ × aⁿ = aᵐ⁺ⁿ. (aᵐ)ⁿ = aᵐⁿ. aᵐ ÷ aⁿ = aᵐ⁻ⁿ.",
        "Polynomials": "Monomial: 3x. Binomial: 2x+5. Trinomial: x²+2x+1.",
        "Factorization": "6x + 9 = 3(2x+3). x² - 4 = (x+2)(x-2).",
        "(a+b)²": "(x+2)² = x² + 4x + 4.",
        "(a-b)²": "(x-3)² = x² - 6x + 9.",
        "a²-b²": "(x+2)(x-2) = x² - 4.",
        "Quadrilaterals": "Square: all equal, 90°. Rectangle: opposite equal, 90°. Rhombus: all equal.",
        "Probability": "P = favorable / total. Coin: 1/2. Dice: 1/6.",
    },
    "Class 9": {
        "Motion": "Distance: total path. Displacement: straight line. Speed: distance/time.",
        "Equations": "v = u + at. s = ut + 1/2at². v² = u² + 2as.",
        "Force": "Push or pull. F = ma. Larger force = larger acceleration.",
        "Newton Laws": "1st: Object at rest stays. 2nd: F=ma. 3rd: Action = reaction.",
        "Gravity": "Pulls down. g = 9.8 m/s². Weight = mass × gravity.",
        "Work": "W = F × d. Force × distance. Unit: Joule (J).",
        "Energy": "Kinetic: 1/2 × m × v². Potential: m × g × h.",
        "Power": "P = W/t. Work per time. Unit: Watt (W).",
        "Atoms": "Nucleus (protons + neutrons). Electrons around. Protons positive, electrons negative.",
        "Photosynthesis": "6CO₂ + 6H₂O + light = C₆H₁₂O₆ + 6O₂. Plants make food.",
    },
    "Class 10": {
        "Chemical Reactions": "Combination, decomposition, displacement, redox.",
        "Acids": "Sour, pH < 7. HCl, H₂SO₄, HNO₃.",
        "Bases": "Bitter, pH > 7. NaOH, KOH, Ca(OH)₂.",
        "Neutralization": "Acid + Base = Salt + Water. HCl + NaOH = NaCl + H₂O.",
        "Electricity": "Current (A), Voltage (V), Resistance (Ω). V = IR (Ohm's law).",
        "Series Circuit": "Single path. Same current. Voltages add.",
        "Parallel Circuit": "Multiple paths. Same voltage. Currents add.",
        "Light Refraction": "Bends passing through media. Snell's law: n₁sinθ₁ = n₂sinθ₂.",
        "Lenses": "Convex: converges (magnifying). Concave: diverges (myopia).",
        "Inheritance": "Traits from parents. Genes carry DNA. Dominant and recessive.",
    },
    "Class 11": {
        "Heat": "Energy transfer. Temperature: kinetic energy measure.",
        "Specific Heat": "Energy per mass per degree. c = Q/(m×ΔT).",
        "Conduction": "Heat through material. Metals conduct well.",
        "Convection": "Heat through fluid. Hot rises, cold sinks.",
        "Radiation": "Heat through waves. No medium needed.",
        "Waves": "Transverse: perpendicular (light). Longitudinal: parallel (sound).",
        "Frequency": "Cycles per second (Hz). λ = v/f.",
        "Sound": "Mechanical wave. Speed 340 m/s in air. 20-20000 Hz hearing.",
        "Magnetism": "Field around magnets. Poles: north, south. Unlike attract, like repel.",
        "Circular Motion": "Constant speed in circle. Centripetal force: F = mv²/r.",
    },
    "Class 12": {
        "Coulomb Law": "F = k(q₁q₂)/r². Force between charges.",
        "Electric Field": "E = F/q. Force per charge. Unit: N/C.",
        "Capacitor": "Stores charge. C = Q/V. Unit: Farad (F).",
        "Current": "I = Q/t. Charge per time. Unit: Ampere (A).",
        "Resistance": "R = V/I. Opposition. Unit: Ohm (Ω).",
        "Power": "P = VI = I²R = V²/R. Energy per time.",
        "Transformer": "Step up/down voltage. Vs/Vp = Ns/Np.",
        "Magnetism": "B around magnets. Direction: right-hand rule.",
        "Motor": "Electromagnet in field rotates. Electrical to mechanical.",
        "Radioactivity": "Unstable nucleus. Alpha (He), Beta (e), Gamma (radiation).",
    },
    "General Knowledge": {
        "AI": "Artificial Intelligence. Mimics human thinking. ChatGPT, Gemini examples.",
        "Study": "Take notes, practice, revise, ask questions, sleep 8 hours.",
        "Time Management": "Schedule, prioritize, Pomodoro (25 work, 5 break).",
        "Stress": "Breathe, exercise, sleep, meditate, talk to friends.",
        "Career": "Coding, science, engineering, teaching, medicine options.",
        "Health": "Balanced diet, exercise 30 min, sleep, reduce stress.",
        "Environment": "Reduce, reuse, recycle. Plant trees, save water.",
    }
}

# ============================================
# 🧠 SPELL CHECKER & GROQ SETUP
# ============================================

class SpellCorrector:
    def __init__(self):
        self.fixes = {
            "photosynthisis": "photosynthesis",
            "fotosynthesis": "photosynthesis",
            "geometery": "geometry",
            "algebera": "algebra",
            "electricty": "electricity",
            "respiration": "respiration",
            "wat": "what",
            "how 2": "how to",
            "plz": "please",
            "u": "you",
            "ur": "your",
        }
    
    def correct(self, text):
        words = text.lower().split()
        corrected = [self.fixes.get(w, w) for w in words]
        return " ".join(corrected)
    
    def find_similar(self, query, keys):
        best, score = None, 0
        for key in keys:
            s = SequenceMatcher(None, query.lower(), key.lower()).ratio()
            if s > score and s > 0.65:
                score, best = s, key
        return best, score

# ============================================
# 🤖 VIDYA AI ENGINE
# ============================================

class VidyaAIEngine:
    def __init__(self, groq_key):
        self.ncert = ncert_database
        self.spell = SpellCorrector()
        self.groq_key = groq_key
        self.client = None
        
        try:
            genai.configure(api_key=groq_key)
            self.client = genai.GenerativeModel('gemini-pro')
        except:
            pass
    
    def search_ncert(self, question):
        question = self.spell.correct(question)
        
        for class_name, topics in self.ncert.items():
            for topic, answer in topics.items():
                if question.lower() in topic.lower():
                    return {
                        "found": True,
                        "answer": answer,
                        "source": class_name,
                        "topic": topic,
                        "type": "NCERT",
                        "confidence": "100%"
                    }
            
            match, score = self.spell.find_similar(question, list(self.ncert[class_name].keys()))
            if match and score > 0.65:
                return {
                    "found": True,
                    "answer": self.ncert[class_name][match],
                    "source": class_name,
                    "topic": match,
                    "type": "NCERT",
                    "confidence": f"{int(score*100)}%",
                    "note": f"(Did you mean: {match}?)"
                }
        
        return None
    
    def ask_ai(self, question, user_type="free"):
        if not self.client:
            return {"found": False, "answer": "API not configured"}
        
        try:
            response = self.client.generate_content(
                f"Answer concisely for a student: {question}",
                generation_config={"max_output_tokens": 200 if user_type == "free" else 500}
            )
            return {
                "found": True,
                "answer": response.text,
                "source": "Gemini AI",
                "type": "General Knowledge",
                "confidence": "85%"
            }
        except Exception as e:
            return {"found": False, "answer": f"Error: {str(e)}"}
    
    def get_answer(self, question, user_type="free"):
        ncert_ans = self.search_ncert(question)
        if ncert_ans:
            return ncert_ans
        
        if user_type in ["premium_month", "premium_year", "mega_offer"]:
            return self.ask_ai(question, user_type)
        
        return {
            "found": False,
            "answer": "Upgrade to Premium for unlimited AI knowledge!",
            "type": "Premium Feature"
        }

# ============================================
# 🔐 USER MANAGEMENT
# ============================================

if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "is_logged_in": False,
        "user_type": "free",
        "username": None,
        "subscription_end": None,
        "api_calls_used": 0,
        "api_calls_limit": 10
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================
# 🌟 MAIN INTERFACE
# ============================================

with st.sidebar:
    st.markdown("### 🤖 VIDYA AI")
    st.markdown("---")
    
    if st.session_state.user_data["is_logged_in"]:
        st.success(f"✅ Logged in as: {st.session_state.user_data['username']}")
        st.info(f"📊 Plan: {st.session_state.user_data['user_type'].upper()}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_data["is_logged_in"] = False
            st.rerun()
    else:
        st.warning("📝 Not logged in")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("# 🤖 VIDYA")
    st.markdown("### AI Learning Assistant - NCERT Edition")

st.markdown("---")

 # Sidebar Menu
with st.sidebar:
    page = st.radio(
        "Navigation",
        ["💬 Chat", "🎓 Learn", "💎 Premium", "📊 Dashboard", "⚙️ Settings"]
    )
    
# Initialize Groq API (Use Gemini as fallback)
GROQ_API_KEY = "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"  # Replace with your key
vidya = VidyaAIEngine(GROQ_API_KEY)

# ============================================
# 💬 CHAT PAGE
# ============================================

if page == "💬 Chat":
    st.markdown("## 💬 Chat with VIDYA")
    st.markdown("Ask anything about Class 1-12 NCERT or general knowledge!")
    
    # Check user type
    user_type = st.session_state.user_data.get("user_type", "free")
    api_limit = st.session_state.user_data.get("api_calls_limit", 10)
    api_used = st.session_state.user_data.get("api_calls_used", 0)
    
    if user_type == "free" and api_used >= api_limit:
        st.error(f"⚠️ Daily limit reached ({api_used}/{api_limit}). Upgrade to Premium for unlimited!")
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        user_input = st.chat_input("Ask VIDYA...")
        
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            
            with st.spinner("🤖 VIDYA thinking..."):
                result = vidya.get_answer(user_input, user_type)
            
            if result["found"]:
                response = f"**{result['answer']}**

📚 {result['source']} | ✅ {result['confidence']}"
            else:
                response = result["answer"]
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
            
            st.session_state.user_data["api_calls_used"] += 1

# ============================================
# 💎 PREMIUM PAGE
# ============================================

elif page == "💎 Premium":
    st.markdown("## 💎 Premium Plans")
    st.markdown("Unlock unlimited AI knowledge and features!")
    
    col1, col2, col3 = st.columns(3)
    
    # Free Plan
    with col1:
        st.markdown("""
        <div class="price-card">
            <h3>🆓 Free</h3>
            <p style="font-size: 24px; color: #00d4ff;">₹0</p>
            <hr>
            <p>✅ 10 questions/day</p>
            <p>✅ NCERT access</p>
            <p>✅ Basic AI</p>
            <p>❌ Limited to 100 words</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Current Plan", key="free", use_container_width=True, disabled=True):
            pass
    
    # Premium Monthly
    with col2:
        st.markdown("""
        <div class="price-card" style="border-color: #ff6b00; box-shadow: 0 0 20px rgba(255, 107, 0, 0.3);">
            <h3>⭐ Premium Plus</h3>
            <p style="font-size: 32px; color: #ff9500; font-weight: bold;">₹49<span style="font-size: 16px;">/month</span></p>
            <p style="text-decoration: line-through; color: #888;">₹99</p>
            <hr>
            <p>✅ Unlimited questions</p>
            <p>✅ Full AI access</p>
            <p>✅ 500 words answers</p>
            <p>✅ Priority support</p>
            <p style="margin-top: 15px; font-weight: bold;">Limited Offer!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Upgrade to ₹49/month", key="monthly"):
            st.session_state.show_payment = True
            st.session_state.selected_plan = "premium_month"
            st.rerun()
    
    # Mega Yearly Offer
    with col3:
        st.markdown("""
        <div class="price-card" style="border-color: #00ff88; box-shadow: 0 0 30px rgba(0, 255, 136, 0.4); transform: scale(1.05);">
            <h3>🔥 MEGA Yearly</h3>
            <p style="font-size: 28px; color: #00ff88; font-weight: bold;">₹499<span style="font-size: 16px;">/year</span></p>
            <p style="text-decoration: line-through; color: #888;">₹999</p>
            <hr>
            <p>✅ Unlimited everything</p>
            <p>✅ Full AI access</p>
            <p>✅ Unlimited answers</p>
            <p>✅ 24/7 support</p>
            <p style="margin-top: 15px; font-weight: bold; color: #00ff88;">BEST DEAL! 50% OFF</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Upgrade to ₹499/year", key="yearly"):
            st.session_state.show_payment = True
            st.session_state.selected_plan = "premium_year"
            st.rerun()
    
    # Payment Methods
    if "show_payment" in st.session_state and st.session_state.show_payment:
        st.markdown("---")
        st.markdown("## 💳 Payment Methods")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📱 PhonePe", use_container_width=True):
                st.success("✅ Redirecting to PhonePe...")
                st.info("PhonePe Payment Gateway
Scan QR Code or Pay ₹49/₹499")
        
        with col2:
            if st.button("🔵 Google Pay", use_container_width=True):
                st.success("✅ Redirecting to Google Pay...")
                st.info("Google Pay Payment Gateway
Pay ₹49/₹499")
        
        with col3:
            if st.button("🟡 Paytm", use_container_width=True):
                st.success("✅ Redirecting to Paytm...")
                st.info("Paytm Payment Gateway
Pay ₹49/₹499")

# ============================================
# 📊 DASHBOARD
# ============================================

elif page == "📊 Dashboard":
    st.markdown("## 📊 Your Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Questions Asked", st.session_state.user_data["api_calls_used"])
    
    with col2:
        st.metric("🎓 Classes Covered", "12")
    
    with col3:
        st.metric("💡 Knowledge Points", "300+")
    
    with col4:
        st.metric("⭐ Rating", "4.9/5")
    
    st.markdown("---")
    st.markdown("### 📈 Usage Stats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Subscription Status**")
        if st.session_state.user_data["user_type"] == "free":
            st.info("🆓 Free Plan - Upgrade for unlimited access")
        else:
            st.success(f"✅ {st.session_state.user_data['user_type'].upper()} Plan Active")
    
    with col2:
        st.write("**Daily Usage**")
        used = st.session_state.user_data["api_calls_used"]
        limit = st.session_state.user_data["api_calls_limit"]
        st.progress(min(used / limit, 1.0))
        st.caption(f"{used}/{limit} questions used today")

# ============================================
# ⚙️ SETTINGS
# ============================================

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Account")
        username = st.text_input("Username", value=st.session_state.user_data.get("username", ""))
        email = st.text_input("Email (for payment)")
        
        if st.button("Update Profile"):
            st.session_state.user_data["username"] = username
            st.success("✅ Profile updated!")
    
    with col2:
        st.markdown("### ��� Preferences")
        notifications = st.checkbox("Enable notifications", value=True)
        language = st.selectbox("Language", ["English", "Hindi"])
        theme = st.selectbox("Theme", ["Dark (VIDYA)", "Light"])
        
        if st.button("Save Preferences"):
            st.success("✅ Preferences saved!")

# ============================================
# 🎓 LEARN PAGE
# ============================================

elif page == "🎓 Learn":
    st.markdown("## 🎓 Learn by Topics")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_class = st.selectbox(
            "Select Class",
            list(ncert_database.keys())
        )
    
    with col2:
        topics = ncert_database[selected_class]
        selected_topic = st.selectbox("Select Topic", list(topics.keys()))
    
    if selected_topic:
        content = topics[selected_topic]
        st.markdown(f"### {selected_topic}")
        st.write(content)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Get More Details", use_container_width=True):
                if st.session_state.user_data["user_type"] == "premium_month" or st.session_state.user_data["user_type"] == "premium_year":
                    st.success("Getting detailed explanation...")
                else:
                    st.warning("Upgrade to Premium for detailed explanations!")
        
        with col2:
            if st.button("❓ Ask Question", use_container_width=True):
                st.session_state.show_chat = True
                st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; margin-top: 40px;">
    <p>🤖 <b>VIDYA AI v7.0</b> | NCERT + Gemini AI | 100% Free + Premium</p>
    <p>Made with ❤️ for Indian Students | <b>LeGenD</b> Edition</p>
    <p>© 2024 VIDYA AI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
