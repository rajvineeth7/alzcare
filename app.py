import streamlit as st
import pandas as pd
import joblib
import base64
import sqlite3
import hashlib
from datetime import datetime
from langchain_groq import ChatGroq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="ALZ CARE",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= ADMIN CONFIG =================
ADMIN_USERNAME = "rajvineeth7@gmail.com"
ADMIN_PASSWORD = "RAJVINEETH7"

# ================= DATABASE =================
conn = sqlite3.connect("alzcare.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    username TEXT,
    result TEXT,
    time TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS chats (
    username TEXT,
    question TEXT,
    answer TEXT,
    time TEXT
)
""")
conn.commit()

# ================= LOAD ML MODEL =================
model = joblib.load("model.joblib")

# ================= SESSION STATE =================
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

def go(page):
    st.session_state.page = page

# ================= PASSWORD HASH =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ================= BACKGROUND (DESKTOP + MOBILE) =================
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html, body, [data-testid="stApp"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: cover;
    }}

    @media only screen and (max-width: 768px) {{
        html, body, [data-testid="stApp"] {{
            background-size: contain;
            background-position: center top;
            background-attachment: scroll;
        }}

        h1 {{ font-size: 34px !important; font-weight: 800; text-align:center; }}
        h2 {{ font-size: 26px !important; font-weight: 700; text-align:center; }}
        h3 {{ font-size: 22px !important; font-weight: 600; text-align:center; }}
        h4 {{ font-size: 20px !important; font-weight: 600; }}

        .stButton>button {{
            width: 100%;
            font-size: 18px;
            padding: 12px;
            border-radius: 10px;
        }}

        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
    }}

    h1,h2,h3,h4,h5,p,label,span {{
        color:black !important;
    }}
    </style>
    """, unsafe_allow_html=True)

set_background("background.png")

# ================= WELCOME (FIXED PAGE) =================
if st.session_state.page == "welcome":

    st.markdown("""
    <style>
    .welcome-container {
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        overflow: hidden;
    }
    </style>

    <div class="welcome-container">
        <h1>Welcome to ALZ CARE</h1>
        <h3>AI-Based Alzheimer’s Risk Prediction & Support</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➡ Enter ALZ CARE"):
        go("login")

# ================= LOGIN =================
elif st.session_state.page == "login":

    st.markdown("<h1>🔐 ALZ CARE Login</h1>", unsafe_allow_html=True)

    st.subheader("👤 User Login / Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login / Create Account"):
        if username and password:
            hashed = hash_password(password)
            user = c.execute("SELECT password FROM users WHERE username=?", (username,)).fetchone()

            if user is None:
                c.execute("INSERT INTO users VALUES (?,?)", (username, hashed))
                conn.commit()
                st.success("Account created successfully")
            elif user[0] != hashed:
                st.error("Incorrect password")
                st.stop()

            st.session_state.username = username
            st.session_state.role = "user"
            go("home")

    st.divider()

    st.subheader("🛠 Admin Login")
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")

    if st.button("Admin Login"):
        if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
            st.session_state.username = admin_user
            st.session_state.role = "admin"
            go("home")
        else:
            st.error("Invalid Admin Credentials")

# ================= HOME =================
elif st.session_state.page == "home":

    st.markdown("<h1>ALZ CARE HOME</h1>", unsafe_allow_html=True)
    st.success(f"Logged in as: {st.session_state.username}")

    if st.button("🧠 About ALZ CARE"): go("about")
    if st.button("🔍 Alzheimer’s Prediction"): go("predict")
    if st.button("💬 Ask Me"): go("chat")
    if st.button("📜 History"): go("history")

    if st.session_state.role == "admin":
        if st.button("🛠 Admin Dashboard"): go("admin")

    if st.button("🚪 Logout"):
        st.session_state.username = None
        st.session_state.role = None
        go("welcome")

# ================= ABOUT (FULL – UNCHANGED) =================
elif st.session_state.page == "about":

    st.markdown("<h1>🧠 About ALZ CARE</h1>", unsafe_allow_html=True)
    st.markdown("""
### What is Alzheimer’s Disease?
Alzheimer’s disease is a progressive neurodegenerative disorder that primarily
affects memory, thinking, learning ability, behavior, and daily functioning.
It is the most common cause of dementia in older adults.

### How Alzheimer’s Disease Develops
The disease is characterized by the accumulation of abnormal proteins
(beta-amyloid plaques and tau tangles) in the brain. These proteins damage neurons,
disrupt communication between brain cells, and eventually lead to brain shrinkage.

### Common Risk Factors
- Increasing age  
- Genetic predisposition  
- Cardiovascular diseases  
- Diabetes and hypertension  
- Obesity and physical inactivity  
- Smoking and alcohol consumption  
- Poor sleep quality  
- Depression and head injuries  

### Purpose of ALZ CARE
ALZ CARE is designed to support **early awareness and risk assessment** of
Alzheimer’s disease using Artificial Intelligence.

### How ALZ CARE Works
- Collects demographic, lifestyle, medical, cognitive, and symptom data  
- Uses a **supervised machine learning model** to analyze patterns  
- Predicts Alzheimer’s risk as **High Risk or Low Risk**  
- Provides educational content and AI-based assistance  

### Key Features
- AI-powered Alzheimer’s risk prediction  
- Simple and user-friendly interface  
- Educational medical information  
- Smart AI assistant for user queries  

⚠ **ALZ CARE is intended for educational and awareness purposes only**
and should not be used as a substitute for professional medical advice or diagnosis.
""")

    st.button("⬅ Back to Home", on_click=go, args=("home",))

# ================= PREDICTION =================
elif st.session_state.page == "predict":

    st.markdown("<h1>🔍 Alzheimer’s Risk Prediction</h1>", unsafe_allow_html=True)

    age = st.slider("Age", 20, 90, 70)
    bmi = st.slider("BMI", 15.0, 40.0, 24.0)
    mmse = st.slider("MMSE", 0, 30, 25)

    if st.button("🔍 Predict Alzheimer’s Risk"):
        if age < 60:
            result_text = "🟢 Low Risk (Screening Only)"
            st.success(result_text)
        else:
            result = model.predict(pd.DataFrame([[age, bmi, mmse]]))[0]
            if result == 1:
                result_text = "🔴 High Risk Detected (Consult Doctor)"
                st.error(result_text)
            else:
                result_text = "🟢 Low Risk Detected"
                st.success(result_text)

        c.execute("INSERT INTO predictions VALUES (?,?,?)",
                  (st.session_state.username, result_text, datetime.now()))
        conn.commit()

    st.button("⬅ Back to Home", on_click=go, args=("home",))

# ================= CHAT =================
elif st.session_state.page == "chat":

    st.markdown("<h1>💬 ALZ CARE Smart Assistant</h1>", unsafe_allow_html=True)
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key="YOUR_GROQ_API_KEY",
        temperature=0.4
    )

    q = st.text_input("Ask your question about Alzheimer’s disease")
    if q:
        response = llm.invoke(q)
        c.execute("INSERT INTO chats VALUES (?,?,?,?)",
                  (st.session_state.username, q, response.content, datetime.now()))
        conn.commit()
        st.markdown(response.content)

    st.button("⬅ Back to Home", on_click=go, args=("home",))

# ================= HISTORY =================
elif st.session_state.page == "history":

    st.markdown("<h1>📜 History</h1>", unsafe_allow_html=True)

    if st.session_state.role == "admin":
        st.dataframe(pd.DataFrame(
            c.execute("SELECT * FROM predictions").fetchall(),
            columns=["Username","Result","Time"]
        ))
        st.dataframe(pd.DataFrame(
            c.execute("SELECT * FROM chats").fetchall(),
            columns=["Username","Question","Answer","Time"]
        ))
    else:
        st.dataframe(pd.DataFrame(
            c.execute("SELECT result,time FROM predictions WHERE username=?",
                      (st.session_state.username,)).fetchall(),
            columns=["Result","Time"]
        ))

    st.button("⬅ Back to Home", on_click=go, args=("home",))

# ================= ADMIN =================
elif st.session_state.page == "admin":

    st.markdown("<h1>🛠 Admin Dashboard</h1>", unsafe_allow_html=True)
    st.metric("Total Users", c.execute("SELECT COUNT(*) FROM users").fetchone()[0])
    st.button("⬅ Back to Home", on_click=go, args=("home",))




