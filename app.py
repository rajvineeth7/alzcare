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

# ================= BACKGROUND (DESKTOP + MOBILE FIX) =================
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

    /* Mobile fix */
    @media only screen and (max-width: 768px) {{
        html, body, [data-testid="stApp"] {{
            background-attachment: scroll;
            background-size: contain;
            background-position: center top;
        }}

        h1 {{ font-size: 30px !important; text-align: center; }}
        h2, h3 {{ font-size: 22px !important; text-align: center; }}
        p, label, span {{ font-size: 16px !important; }}

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

# ================= WELCOME =================
if st.session_state.page == "welcome":

    st.markdown("""
    <div style="height:80vh;display:flex;flex-direction:column;
                justify-content:center;align-items:center;text-align:center;">
        <h1 style="font-weight:800;">Welcome to ALZ CARE</h1>
        <h3>AI-Based Alzheimer’s Risk Prediction & Support</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➡ Enter ALZ CARE"):
        go("login")

# ================= LOGIN (MOBILE STACKED) =================
elif st.session_state.page == "login":

    st.markdown("<h1 style='text-align:center;'>🔐 ALZ CARE Login</h1>", unsafe_allow_html=True)

    st.subheader("👤 User Login / Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login / Create Account"):
        if username and password:
            hashed = hash_password(password)
            user = c.execute(
                "SELECT password FROM users WHERE username=?",
                (username,)
            ).fetchone()

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

    st.markdown("<h1 style='text-align:center;'>ALZ CARE HOME</h1>", unsafe_allow_html=True)
    st.success(f"Logged in as: {st.session_state.username}")

    if st.button("🧠 About ALZ CARE"): go("about")
    if st.button("🔍 Alzheimer’s Prediction"): go("predict")
    if st.button("💬 Ask Me"): go("chat")
    if st.button("📜 History"): go("history")

    if st.session_state.role == "admin":
        if st.button("🛠 Admin Dashboard"):
            go("admin")

    if st.button("🚪 Logout"):
        st.session_state.username = None
        st.session_state.role = None
        go("welcome")

# ================= ABOUT =================
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
    gender = 1 if st.selectbox("Gender", ["Female","Male"])=="Male" else 0
    ethnicity = st.selectbox("Ethnicity Group", [0,1,2,3])
    education = ["No Formal Education","Primary","Secondary","Higher Education"].index(
        st.selectbox("Education Level",
        ["No Formal Education","Primary","Secondary","Higher Education"])
    )

    bmi = st.slider("BMI",15.0,40.0,24.0)
    smoking = 1 if st.selectbox("Smoking",["No","Yes"])=="Yes" else 0
    alcohol = 1 if st.selectbox("Alcohol",["No","Yes"])=="Yes" else 0
    physical = 1 if st.selectbox("Physical Activity",["No","Yes"])=="Yes" else 0
    diet = ["Poor","Average","Good"].index(st.selectbox("Diet Quality",["Poor","Average","Good"]))
    sleep = ["Poor","Average","Good"].index(st.selectbox("Sleep Quality",["Poor","Average","Good"]))

    family = 1 if st.selectbox("Family History of Alzheimer’s",["No","Yes"])=="Yes" else 0
    cardio = 1 if st.selectbox("Cardiovascular Disease",["No","Yes"])=="Yes" else 0
    diabetes = 1 if st.selectbox("Diabetes",["No","Yes"])=="Yes" else 0
    depression = 1 if st.selectbox("Depression",["No","Yes"])=="Yes" else 0
    head = 1 if st.selectbox("Head Injury",["No","Yes"])=="Yes" else 0
    hyper = 1 if st.selectbox("Hypertension",["No","Yes"])=="Yes" else 0

    sys = st.slider("Systolic BP",90,180,120)
    dia = st.slider("Diastolic BP",60,120,80)
    chol = st.slider("Total Cholesterol",120,300,180)
    ldl = st.slider("LDL",50,200,100)
    hdl = st.slider("HDL",30,100,50)
    tg = st.slider("Triglycerides",50,400,150)

    mmse = st.slider("MMSE",0,30,25)
    func = st.slider("Functional Assessment",0,10,7)
    adl = st.slider("ADL",0,10,8)

    mem = 1 if st.selectbox("Memory Complaints",["No","Yes"])=="Yes" else 0
    beh = 1 if st.selectbox("Behavioral Problems",["No","Yes"])=="Yes" else 0
    conf = 1 if st.selectbox("Confusion",["No","Yes"])=="Yes" else 0
    dis = 1 if st.selectbox("Disorientation",["No","Yes"])=="Yes" else 0
    pers = 1 if st.selectbox("Personality Changes",["No","Yes"])=="Yes" else 0
    task = 1 if st.selectbox("Difficulty Completing Tasks",["No","Yes"])=="Yes" else 0
    forg = 1 if st.selectbox("Forgetfulness",["No","Yes"])=="Yes" else 0

    if st.button("🔍 Predict Alzheimer’s Risk"):

        if age < 35:
            result_text = "🟢 Low Risk — Maintain a healthy lifestyle."
            st.success(result_text)

        elif 35 <= age < 60:
            if any([bmi>=30, sys>=140, dia>=90, mmse<=20, adl<=3]):
                result_text = (
                    "🟡 Possible Increased Risk in the Future (Screening Result)\n\n"
                    "⚠ This is for awareness only and not a diagnosis."
                )
                st.warning(result_text)
            else:
                result_text = "🟢 Low Risk — Continue healthy habits."
                st.success(result_text)

        else:
            data = pd.DataFrame([[age,gender,ethnicity,education,bmi,smoking,alcohol,physical,
                                  diet,sleep,family,cardio,diabetes,depression,head,hyper,
                                  sys,dia,chol,ldl,hdl,tg,mmse,func,adl,
                                  mem,beh,conf,dis,pers,task,forg]])
            result = model.predict(data)[0]

            if result == 1:
                result_text = "🔴 High Risk Detected\n\n⚠ Not a diagnosis."
                st.error(result_text)
            else:
                result_text = "🟢 Low Risk Detected\n\nRegular check-ups advised."
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
        api_key="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",
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



