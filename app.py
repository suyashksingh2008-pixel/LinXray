import json
import time
import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image
import sqlite3

# Page Title
st.set_page_config(page_title="LinXray", page_icon="assets/altlogo.png")

# Database Functions for URL queue
def streamlit_to_scanner_create():
    con = sqlite3.connect("users.db")
    c = con.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS TO_SCANS (
            USERNAME TEXT NOT NULL,
            TARGET_URL TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

def streamlit_to_scanner_save(username, target_url):
    con = sqlite3.connect("users.db")
    c = con.cursor()
    c.execute("INSERT INTO TO_SCANS (USERNAME, TARGET_URL) VALUES (?, ?)", (username, target_url))
    con.commit()
    con.close()

# Initialize scan queue table on startup
streamlit_to_scanner_create()

# Login
def User_Login():
    credentials = {"usernames": {}}
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                name TEXT,
                password TEXT
            )
        """)
        cursor.execute("SELECT username, name, password FROM users")
        rows = cursor.fetchall()
        conn.close()

        for username, name, password in rows:
            credentials["usernames"][username] = {
                "name": name,
                "password": password,
                "logged_in": False
            }
    except Exception as e:
        st.warning(f"Database note: {e}")
        
    return credentials

def register_user_in_db(username, name, hashed_password):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, name, password) VALUES (?, ?, ?)",
            (username, name, hashed_password)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

# Saving cookie of user being logged in
credentials = User_Login()

authenticator = stauth.Authenticate(
    credentials,
    cookie_name="app_cookie",
    key="super_secret_key",
    cookie_expiry_days=30
)

# Login Page state initialization
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "Login"

# Custom CSS: Border styling and completely hiding the default built-in form headers
st.markdown(
    """
    <style>
    [data-testid="stForm"] {
        border: 3px solid #b32121 !important;
        border-radius: 12px;
    }
    [data-testid="stForm"] h1, 
    [data-testid="stForm"] h2, 
    [data-testid="stForm"] h3 {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- IF USER IS LOGGED IN ---
if st.session_state.get("authentication_status"):
    try:
        Suyash = Image.open("assets/Suyash.png")
        Jonathan = Image.open("assets/jnthn.png")
        Ayush = Image.open("assets/aysh.png")
        Gauresh = Image.open("assets/grs.png")
    except FileNotFoundError:
        pass
    
    # Left to right Sidebar Gradient
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(to right, #2C325B, #2C325B00);
        }
        [data-testid="stSidebar"] .stButton button {
            background-color: #1A1D36;
            color: #ffffff;
            border: 2px solid #3F4464;
            border-radius: 8px;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background-color: #2C325B;
            border-color: #b32121;
            color: #00FFE5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Sidebar
    authenticator.logout("Logout", "sidebar")
    st.sidebar.space(10)
    st.sidebar.write(f"Welcome, {st.session_state.get('name', 'User')}!")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("History")
    
    current_username = st.session_state.get("username")
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TARGET_URL FROM TO_SCANS 
            WHERE USERNAME = ? 
            GROUP BY TARGET_URL 
            ORDER BY MAX(rowid) DESC LIMIT 10
        """, (current_username,))
        history_rows = cursor.fetchall()
        conn.close()
        
        if history_rows:
            for idx, (logged_url,) in enumerate(history_rows):
                display_label = logged_url if len(logged_url) < 30 else logged_url[:27] + "..."
                if st.sidebar.button(display_label, key=f"history_btn_{idx}", use_container_width=True):
                    st.session_state["target_url_input"] = logged_url
                    st.session_state["show_results"] = True
                    st.rerun()
        else:
            st.sidebar.caption("No search history yet.")
    except Exception as e:
        st.sidebar.caption("Could not load history.")

    # Header
    st.markdown("""
    <div style="text-align: center; width: 100%;">
        <h1 style="font-family: 'Orbitron', sans-serif; font-size: 4rem; display: block; width: 100%; margin: 0 auto;">
        Welcome to LinXray
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <hr style="
            border: none;
            height: 3px;
            background-color: #2E314A;
            width: 130%;
            margin-left: -20%;
            margin-top: 20px;
            margin-bottom: 20px;
        ">
    """, unsafe_allow_html=True)
    st.space(30)
    
    if "show_results" not in st.session_state:
        st.session_state["show_results"] = False

    c1, c2, c3 = st.columns([0.5, 3, 0.5])
    with c2:
        with st.form("url_scan_form", clear_on_submit=False):
            target_url = st.text_input("Enter URL", placeholder="https://example.com", label_visibility="collapsed")
            submit_scan = st.form_submit_button("Start Scan", use_container_width=True)
            
        if submit_scan:
            if target_url.strip():
                # Loading bar implementation based on wireframe
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.01) # Simulate scanning delay
                    progress_bar.progress(percent_complete + 1)
                progress_bar.empty()

                current_username = st.session_state.get("username")
                streamlit_to_scanner_save(current_username, target_url)
                st.session_state["show_results"] = True  
            else:
                st.warning("Please enter a valid URL.")

    # ANALYSIS RESULTS 
    if st.session_state.get("show_results"):
        st.space(20)
        
        st.markdown("""
            <hr style="border: none; height: 1px; background-color: #2E314A; width: 100%; margin-top: 20px; margin-bottom: 20px;">
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align: center; width: 100%;">
                <h1 style="font-size: 2.5rem; display: block; margin: 0 auto; font-weight: normal;">
                Analysis Results
                </h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <hr style="border: none; height: 1px; background-color: #2E314A; width: 60%; margin: 20px auto;">
        """, unsafe_allow_html=True)

        # Parsed structured data mimicking the JSON pull from database.py
        scan_results = {
            "deceptive_elements": "The malicious webpage relies heavily on brand impersonation and dark patterns to deceive the target into believing they are interacting with an official Amazon portal. Observed domain utilizes a `.club` generic top-level domain frequently associated with low-cost infrastructure. Includes spoofed brand logos and fabricated UI section titles.",
            "phishing_indicators": "The site employs classic social engineering techniques designed to bypass critical thinking through lure-and-urgency mechanics. This includes artificial urgency tactics like dynamic countdown timers, and high-value lure/reward scams offering items like a $1000 Amazon Gift Card in exchange for answering a short survey.",
            "risk_assessment": {
                "risk_index": "98/100",
                "classification": "CRITICAL / HIGH RISK",
                "recommended_action": "Block access to the top-level domain `.club` or specifically blackhole `rewardinheaven.club` and associated IP infrastructure at the DNS/Secure Web Gateway level."
            }
        }

        # Wireframe Layout matching
        st.markdown("### Deceptive elements:")
        st.write(scan_results["deceptive_elements"])
        
        st.space(20)

        st.markdown("### Phishing & Behavioral Indicators:")
        st.write(scan_results["phishing_indicators"])
        
        st.space(20)

        st.markdown("### Final Risk Assessment:")
        st.markdown(f"Risk Index : {scan_results['risk_assessment']['risk_index']}")
        st.markdown(f"Threat Classification : {scan_results['risk_assessment']['classification']}")
        st.markdown(f"Recommended Action : {scan_results['risk_assessment']['recommended_action']}")

    st.space(40)

    # ====================================================
    # MEET THE TEAM SECTION (ALWAYS VISIBLE WHEN LOGGED IN)
    # ====================================================
    
    st.markdown("""
        <hr style="
            border: none;
            height: 3px;
            background-color: #b32121;
            width: 150%;
            margin-left: -25%;
            margin-top: 20px;
            margin-bottom: 20px;
        ">
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center;">
            <h1 style="
                font-family: 'Orbitron',sans-serif;
                font-size: 2.5rem;
                white-space: nowrap; 
                display: inline-block;
            ">
            Meet the Team!
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
        <hr style="
            border: none;
            height: 3px;
            background-color: #2E314A;
            width: 100%;
            margin-left: 0%;
            margin-top: 20px;
            margin-bottom: 20px;
        ">
    """, unsafe_allow_html=True)
        
    cl11, space1, cl12 = st.columns([2, 2.5, 3])
    with cl11:
        if 'Suyash' in locals(): st.image(Suyash)
        st.write("---")
        if 'Jonathan' in locals(): st.image(Jonathan)
        st.write("---")
        if 'Ayush' in locals(): st.image(Ayush)
        st.write("---")
        if 'Gauresh' in locals(): st.image(Gauresh)
        
    with cl12:
        st.space(10)
        st.markdown("""
            <div style="display:flex; align-items:baseline;gap:15px;flex-wrap:wrap;margin-top:10px;">
                <h3 style="white-space: nowrap; margin: 0; font-size: 1.5rem;">
                    <a href="#" style="color: #00FFE5; text-decoration: underline;">Suyash Kumar Singh</a>
                </h3>
                <span style="font-size: 1.1rem; color: inherit;">Database Management</span>
            </div>
        """, unsafe_allow_html=True)
        st.space(35)
        st.write("---")
        st.space(5)
        st.markdown("""
            <div style="display:flex; align-items:baseline;gap:15px;flex-wrap:wrap;margin-top:10px;">
                <h3 style="white-space: nowrap; margin: 0; font-size: 1.5rem;">
                    <a href="https://www.linkedin.com/in/jonathan-karan-kamal-690766229/" style="color: #00FFE5; text-decoration: underline;">Jonathan Karan Kamal</a>
                </h3>
                <span style="font-size: 1.1rem; color: inherit;">Virtual Environment Testing and Isolation</span>
            </div>
        """, unsafe_allow_html=True)
        st.space(20)
        st.write("---")
        st.space(5)
        st.markdown("""
            <div style="display:flex; align-items:baseline;gap:15px;flex-wrap:wrap;margin-top:10px;">
                <h3 style="white-space: nowrap; margin: 0; font-size: 1.5rem;">
                    <a href="#" style="color: #00FFE5; text-decoration: underline;">Ayush Kumar</a>
                </h3>
                <span style="font-size: 1.1rem; color: inherit;">Threat Intelligence System</span>
            </div>
        """, unsafe_allow_html=True)
        st.space(45)
        st.write("---")
        st.space(60)
        st.markdown("""
            <div style="display:flex; align-items:baseline;gap:15px;flex-wrap:wrap;margin-top:10px;">
                <h3 style="white-space: nowrap; margin: 0; font-size: 1.5rem;">
                    <a href="#" style="color: #00FFE5; text-decoration: underline;">Gauresh Nitin Bhatia</a>
                </h3>
                <span style="font-size: 1.1rem; color: inherit;">UI/UX & Front End</span>
            </div>
        """, unsafe_allow_html=True)
    st.write("---")

# --- IF LOGIN FAILED ---
elif st.session_state.get("authentication_status") is False:
    st.error("Username/password is incorrect")
    st.session_state["auth_mode"] = "Login"
    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
    try:
        authenticator.login(location="main", key="unique_login_form_failed")
    except Exception as e:
        st.error(f"Authenticator error: {e}")
    st.markdown("---")
    if st.button("Need an account? Sign Up", use_container_width=True):
        st.session_state["auth_mode"] = "Sign Up"
        st.rerun()

# --- IF USER IS NOT LOGGED IN ---
elif st.session_state.get("authentication_status") is None:
    if st.session_state["auth_mode"] == "Login":
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        try:
            authenticator.login(location="main", key="unique_login_form_none")
        except Exception as e:
             st.error(f"Authenticator error: {e}")
        st.space(10)
        if st.button("Need an account? Sign Up", use_container_width=True):
            st.session_state["auth_mode"] = "Sign Up"
            st.rerun()
            
    elif st.session_state["auth_mode"] == "Sign Up":
        st.markdown("<h2 style='text-align: center;'>Create a New Account</h2>", unsafe_allow_html=True)
        with st.form("signup_form"):
            new_name = st.text_input("Full Name")
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Register")
            
        if submit:
            if not new_username or not new_password or not new_name:
                st.warning("Please fill out all required fields.")
            else:
                hashed_pw = stauth.Hasher.hash(new_password)
                if register_user_in_db(new_username, new_name, hashed_pw):
                    st.success("Account created! Switch back to Login to sign in.")
                else:
                    st.error("Username already exists or database error.")
                    
        st.markdown("---")
        if st.button("Already have an account? Login", use_container_width=True):
            st.session_state["auth_mode"] = "Login"
            st.rerun()