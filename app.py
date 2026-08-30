import json
import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image
import sqlite3

# Page Title
st.set_page_config(page_title="LinXray", page_icon="assets/logo.png")

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
    """Fetches users from SQLite and guarantees the structure matches streamlit-authenticator requirements."""
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
    /* Custom border styling for the login form */
    [data-testid="stForm"] {
        border: 3px solid #b32121 !important;
        border-radius: 12px;
    }
    
    /* Hides the built-in header/title inside the authenticator form */
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
    # Loading assets (Ensure these images exist in your assets folder to prevent FileNotFoundError)
    try:
        Suyash = Image.open("assets/Suyash.png")
        Jonathan = Image.open("assets/jnthn.png")
        Ayush = Image.open("assets/aysh.png")
        Gauresh = Image.open("assets/grs.png")
    except FileNotFoundError:
        st.warning("One or more team images are missing from the 'assets/' folder.")
    
    # Left to right Sidebar Gradient
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(to right, #2C325B, #2C325B00);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Main page content
    # Sidebar
    authenticator.logout("Logout", "sidebar")
    st.sidebar.write(f"Welcome, {st.session_state.get('name', 'User')}!")

    # Header
    st.markdown("""
    <div style="text-align: center; width: 100%;">
        <h1 style="
            font-family: 'Orbitron', sans-serif;
            font-size: 4rem;
            display: block;
            width: 100%;
            margin: 0 auto;
        ">
        Welcome to LinXray
        </h1>
    </div>
    """, unsafe_allow_html=True)
    st.space(30)
    
    # Initialize the results visibility flag in session state if not present
    if "show_results" not in st.session_state:
        st.session_state["show_results"] = False

    c1, c2, c3 = st.columns([0.5, 3, 0.5])
    with c2:
        with st.form("url_scan_form", clear_on_submit=False):
            target_url = st.text_input("Enter URL", placeholder="https://example.com", label_visibility="collapsed")
            submit_scan = st.form_submit_button("Start Scan", use_container_width=True)
            
        if submit_scan:
            if target_url.strip():
                current_username = st.session_state.get("username")
                streamlit_to_scanner_save(current_username, target_url)
                st.session_state["show_results"] = True  # Reveals the results section
                st.success(f"URL submitted for scanning: {target_url}")
            else:
                st.warning("Please enter a valid URL.")

    # --- ANALYSIS RESULTS SECTION (Only shows after submit) ---
    if st.session_state.get("show_results"):
        st.space(20)
        
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
            <div style="text-align: center; width: 100%;">
                <h1 style="
                    font-family: 'Orbitron', sans-serif;
                    font-size: 3rem;
                    display: block;
                    width: 100%;
                    margin: 0 auto;
                ">
                Analysis Results
                </h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <hr style="
                border: none;
                height: 3px;
                background-color: #2E314A;
                width: 110%;
                margin-left: -10%;
                margin-top: 20px;
                margin-bottom: 20px;
            ">
        """, unsafe_allow_html=True)

        # Loading the JSON data natively (Replace this dict with a file load if querying from backend)
        scan_results = {
            "scan_id": "096ec959-cd50-414c-b0f2-1369ec6d5b22",
            "target_url": "https://hyeonseok067.gitbuh.io/Netflix",
            "maximum_actions": 10,
            "buttons_found": 13,
            "buttons_tested": 4,
            "actions": [
                {
                    "action_number": 1,
                    "button_label": "About Us",
                    "status": "completed",
                    "url_before": "https://hyeonseok067.gitbuh.io/Netflix",
                    "url_after": "https://adorarama.com/about-us.php",
                    "before_screenshot": "action_01_about_us_before.png",
                    "after_screenshot": "action_01_about_us_after.png",
                    "error": None
                },
                {
                    "action_number": 2,
                    "button_label": "Contact Us",
                    "status": "failed",
                    "url_before": "https://hyeonseok067.gitbuh.io/Netflix",
                    "url_after": None,
                    "before_screenshot": "action_02_contact_us_before.png",
                    "after_screenshot": None,
                    "error": "Page.screenshot: Timeout 5000ms exceeded.\nCall log:\n  - taking page screenshot\n  - waiting for fonts to load...\n  - fonts loaded\n"
                },
                {
                    "action_number": 3,
                    "button_label": "Privacy Policy",
                    "status": "completed",
                    "url_before": "https://hyeonseok067.gitbuh.io/Netflix",
                    "url_after": "https://adorarama.com/privacy-policy.php",
                    "before_screenshot": "action_03_privacy_policy_before.png",
                    "after_screenshot": "action_03_privacy_policy_after.png",
                    "error": None
                },
                {
                    "action_number": 4,
                    "button_label": "Terms of Service",
                    "status": "completed",
                    "url_before": "https://hyeonseok067.gitbuh.io/Netflix",
                    "url_after": "https://adorarama.com/terms-of-service.php",
                    "before_screenshot": "action_04_terms_of_service_before.png",
                    "after_screenshot": "action_04_terms_of_service_after.png",
                    "error": None
                }
            ],
            "skipped_buttons": [
                {"original_index": 0, "label": "Events and Attractions", "permitted": False, "reason": "Blocked non-web link"},
                {"original_index": 1, "label": "Television", "permitted": False, "reason": "Blocked non-web link"},
                {"original_index": 2, "label": "Music and Audio", "permitted": False, "reason": "Blocked non-web link"},
                {"original_index": 3, "label": "Technology & Computing", "permitted": False, "reason": "Blocked non-web link"},
                {"original_index": 4, "label": "Hobbies & Interests", "permitted": False, "reason": "Blocked non-web link"},
                {"original_index": 5, "label": "Automotive", "permitted": False, "reason": "Blocked non-web link"},
                {"original_index": 6, "label": "Communication", "permitted": False, "reason": "Blocked non-web link"},
                {"original_index": 7, "label": "Shopping", "permitted": False, "reason": "Blocked non-web link"},
                {"original_index": 8, "label": "Education", "permitted": False, "reason": "Blocked non-web link"}
            ]
        }

        # Scan Overview Section
        st.subheader("🔍 Scan Overview")
        st.markdown(f"**Target Analyzed:** `{scan_results['target_url']}`")
        st.caption(f"Scan ID: {scan_results['scan_id']}")
        
        st.space(10)
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Buttons Found", scan_results["buttons_found"])
        with m2:
            st.metric("Buttons Successfully Tested", scan_results["buttons_tested"])
        with m3:
            st.metric("Action Limit", scan_results["maximum_actions"])

        st.space(20)

        # Detailed Actions Section
        st.subheader("🎯 Tested Elements Breakdown")
        
        for action in scan_results["actions"]:
            status_emoji = "✅" if action["status"] == "completed" else "❌"
            expander_title = f"{status_emoji} Action {action['action_number']}: {action['button_label']} "
            
            with st.expander(expander_title):
                if action["status"] == "completed":
                    st.success("Execution: Completed Successfully")
                    st.markdown(f"**Origin URL:** `{action['url_before']}`")
                    st.markdown(f"**Redirected To:** `{action['url_after']}`")
                else:
                    st.error("Execution: Failed")
                    st.markdown(f"**Origin URL:** `{action['url_before']}`")
                    st.code(f"Error Log:\n{action['error']}", language="bash")

        st.space(20)

        # Skipped Buttons Section
        st.subheader("⚠️ Skipped Elements")
        with st.expander("View Skipped Buttons"):
            for skipped in scan_results["skipped_buttons"]:
                st.markdown(f"- **{skipped['label']}** — *Reason: {skipped['reason']}*")

    st.space(20)
    
    # Custom colored and extended divider line for Meet the Team section
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

    # Meet the Team
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
        
    cl11, space1, cl12 = st.columns([2, 2.5, 3])
    with cl11:
        # Note: Wrapped in try-except earlier so this doesn't crash if files are missing
        if 'Suyash' in locals(): st.image(Suyash)
        if 'Jonathan' in locals(): st.image(Jonathan)
        if 'Ayush' in locals(): st.image(Ayush)
        if 'Gauresh' in locals(): st.image(Gauresh)
        
    with cl12:
        st.space(10)
        st.markdown("""
                    <div style="display:flex; align-items:baseline;gap:15px;flex-wrap:wrap;margin-top:10px;">
                        <h3 style="white-space: nowrap; margin: 0; font-size: 1.5rem;">
                            <a href="#"
                                style="color: #00FFE5; text-decoration: underline;">
                                 Suyash Kumar Singh
                            </a>
                        </h3>
                        <span style="font-size: 1.1rem; color: inherit;">Database Management</span>
                    </div>
                """, unsafe_allow_html=True)
        st.space(85)
        st.markdown("""
            <div style="display:flex; align-items:baseline;gap:15px;flex-wrap:wrap;margin-top:10px;">
                <h3 style="white-space: nowrap; margin: 0; font-size: 1.5rem;">
                    <a href="https://www.linkedin.com/in/jonathan-karan-kamal-690766229/"
                        style="color: #00FFE5; text-decoration: underline;">
                         Jonathan Karan Kamal
                    </a>
                </h3>
                <span style="font-size: 1.1rem; color: inherit;">Virtual Environment Testing and Isolation</span>
            </div>
        """, unsafe_allow_html=True)
        st.space(57)
        st.markdown("""
                    <div style="display:flex; align-items:baseline;gap:15px;flex-wrap:wrap;margin-top:10px;">
                        <h3 style="white-space: nowrap; margin: 0; font-size: 1.5rem;">
                            <a href="#"
                                style="color: #00FFE5; text-decoration: underline;">
                                 Ayush Kumar
                            </a>
                        </h3>
                        <span style="font-size: 1.1rem; color: inherit;">Threat Intelligence System</span>
                    </div>
                """, unsafe_allow_html=True)
        st.space(60)
        st.markdown("""
                            <div style="display:flex; align-items:baseline;gap:15px;flex-wrap:wrap;margin-top:10px;">
                                <h3 style="white-space: nowrap; margin: 0; font-size: 1.5rem;">
                                    <a href="#"
                                        style="color: #00FFE5; text-decoration: underline;">
                                         Gauresh Nitin Bhatia
                                    </a>
                                </h3>
                                <span style="font-size: 1.1rem; color: inherit;">UI/UX & Front End</span>
                            </div>
                        """, unsafe_allow_html=True)

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

# --- IF USER IS NOT LOGGED IN (Status is None) ---
elif st.session_state.get("authentication_status") is None:
    
    # Show Login form ONLY when auth_mode is Login
    if st.session_state["auth_mode"] == "Login":
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        try:
            authenticator.login(location="main", key="unique_login_form_none")
        except Exception as e:
             st.error(f"Authenticator error: {e}")
        st.space(10)
        st.markdown("""
                <hr style="
                    border: none;
                    height: 3px;
                    background-color: #3F4464;
                    width: 100%;
                    margin: 0 auto;
                ">
            """, unsafe_allow_html=True)
        st.space(20)
        if st.button("Need an account? Sign Up", use_container_width=True):
            st.session_state["auth_mode"] = "Sign Up"
            st.rerun()
            
    # Show Sign Up form ONLY when auth_mode is Sign Up
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