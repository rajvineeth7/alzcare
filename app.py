import streamlit as st
import pandas as pd
import joblib
import base64
import sqlite3
import hashlib
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# ================= PAGE CONFIG =================
st.set_page_config(page_title="ALZ CARE", layout="wide")

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
if "page" not in st.session_state: st.session_state.page = "welcome"
if "username" not in st.session_state: st.session_state.username = None
if "role" not in st.session_state: st.session_state.role = None

def go(page):
    st.session_state.page = page

# ================= PASSWORD HASH =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ================= BACKGROUND =================
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
    html, body, [data-testid="stApp"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
    }}
    h1,h2,h3,h4,h5,p,label,span {{ color:black !important; }}
    </style>
    """, unsafe_allow_html=True)

set_background("background.png")

# ================= WELCOME PAGE =================
if st.session_state.page == "welcome":

    st.markdown("""
    <div style="height:85vh;display:flex;flex-direction:column;
                justify-content:center;align-items:center;text-align:center;">
        <h1 style="font-size:64px;font-weight:800;">Welcome to ALZ CARE</h1>
        <h3>AI-Based Alzheimer’s Risk Prediction & Support</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➡ Enter ALZ CARE"):
        go("login")

# ================= LOGIN PAGE =================
elif st.session_state.page == "login":

    st.markdown("<h1 style='text-align:center;'>🔐 ALZ CARE Login</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # ---------- USER LOGIN ----------
    with col1:
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
            else:
                st.warning("Please enter username and password")

    # ---------- ADMIN LOGIN ----------
    with col2:
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

# ================= ABOUT PAGE (UNCHANGED CONTENT) =================
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

⚠ ALZ CARE is intended for **educational and awareness purposes only**
and should not be used as a substitute for professional medical advice or diagnosis.
""")

    st.button("⬅ Back to Home", on_click=go, args=("home",))

# ================= PREDICTION PAGE (ML ONLY) =================
elif st.session_state.page == "predict":

    st.markdown("<h1>🔍 Alzheimer’s Risk Prediction</h1>", unsafe_allow_html=True)

    # -------- Demographics --------
    age = st.slider("Age", 60, 90, 70)
    gender = st.selectbox("Gender", ["Female", "Male"])
    ethnicity = st.selectbox("Ethnicity Group", [0,1,2,3])
    education = st.selectbox(
        "Education Level",
        ["No Formal Education","Primary","Secondary","Higher Education"]
    )

    gender = 1 if gender=="Male" else 0
    education = ["No Formal Education","Primary","Secondary","Higher Education"].index(education)

    # -------- Lifestyle --------
    bmi = st.slider("BMI",15.0,40.0,24.0)
    smoking = st.selectbox("Smoking",["No","Yes"])
    alcohol = st.selectbox("Alcohol",["No","Yes"])
    physical = st.selectbox("Physical Activity",["No","Yes"])
    diet = st.selectbox("Diet Quality",["Poor","Average","Good"])
    sleep = st.selectbox("Sleep Quality",["Poor","Average","Good"])

    smoking,alcohol,physical = map(lambda x:1 if x=="Yes" else 0,[smoking,alcohol,physical])
    diet = ["Poor","Average","Good"].index(diet)
    sleep = ["Poor","Average","Good"].index(sleep)

    # -------- Medical History --------
    family = st.selectbox("Family History of Alzheimer’s",["No","Yes"])
    cardio = st.selectbox("Cardiovascular Disease",["No","Yes"])
    diabetes = st.selectbox("Diabetes",["No","Yes"])
    depression = st.selectbox("Depression",["No","Yes"])
    head = st.selectbox("Head Injury",["No","Yes"])
    hyper = st.selectbox("Hypertension",["No","Yes"])

    family,cardio,diabetes,depression,head,hyper = map(
        lambda x:1 if x=="Yes" else 0,
        [family,cardio,diabetes,depression,head,hyper]
    )

    # -------- Vitals --------
    sys = st.slider("Systolic BP",90,180,120)
    dia = st.slider("Diastolic BP",60,120,80)
    chol = st.slider("Total Cholesterol",120,300,180)
    ldl = st.slider("LDL",50,200,100)
    hdl = st.slider("HDL",30,100,50)
    tg = st.slider("Triglycerides",50,400,150)

    # -------- Cognitive --------
    mmse = st.slider("MMSE",0,30,25)
    func = st.slider("Functional Assessment",0,10,7)
    adl = st.slider("ADL",0,10,8)

    # -------- Symptoms --------
    mem = st.selectbox("Memory Complaints",["No","Yes"])
    beh = st.selectbox("Behavioral Problems",["No","Yes"])
    conf = st.selectbox("Confusion",["No","Yes"])
    dis = st.selectbox("Disorientation",["No","Yes"])
    pers = st.selectbox("Personality Changes",["No","Yes"])
    task = st.selectbox("Difficulty Completing Tasks",["No","Yes"])
    forg = st.selectbox("Forgetfulness",["No","Yes"])

    mem,beh,conf,dis,pers,task,forg = map(
        lambda x:1 if x=="Yes" else 0,
        [mem,beh,conf,dis,pers,task,forg]
    )

    if st.button("🔍 Predict Alzheimer’s Risk"):
        data = pd.DataFrame([[age,gender,ethnicity,education,bmi,smoking,alcohol,physical,
                              diet,sleep,family,cardio,diabetes,depression,head,hyper,
                              sys,dia,chol,ldl,hdl,tg,mmse,func,adl,
                              mem,beh,conf,dis,pers,task,forg]])

        result = model.predict(data)[0]

        c.execute(
            "INSERT INTO predictions VALUES (?,?,?)",
            (st.session_state.username,
             "High Risk" if result==1 else "Low Risk",
             datetime.now())
        )
        conn.commit()

        if result == 1:
            st.error(
                "⚠ **High Risk Detected**\n\n"
                "The model indicates a higher likelihood of developing Alzheimer’s disease.\n"
                "**Strongly advised to consult a neurologist or physician.**"
            )
        else:
            st.success(
                "✅ **Low Risk Detected**\n\n"
                "Lower likelihood detected.\n"
                "**Maintain a healthy lifestyle and consult a doctor for confirmation.**"
            )

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
        st.subheader("My Predictions")
        for r in c.execute("SELECT result,time FROM predictions WHERE username=?",
                           (st.session_state.username,)):
            st.write(r)

        st.subheader("My Chats")
        for q,a,t in c.execute("SELECT question,answer,time FROM chats WHERE username=?",
                               (st.session_state.username,)):
            st.write("Q:",q)
            st.write("A:",a)

    st.button("⬅ Back to Home", on_click=go, args=("home",))

# ================= ADMIN DASHBOARD =================
elif st.session_state.page == "admin":

    st.markdown("<h1>🛠 Admin Dashboard</h1>", unsafe_allow_html=True)

    st.metric("Total Users", c.execute("SELECT COUNT(*) FROM users").fetchone()[0])

    st.button("🏠 Go to Home", on_click=go, args=("home",))

