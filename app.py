import json
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_lottie import st_lottie
from PIL import Image
import sqlite3

#Page Title
st.set_page_config(page_title="LinXray", page_icon="assets/logo.png")

#Login
def User_Login():
    """Fetches users from SQLite and guarantees the test user works."""
    credentials = {"usernames": {}}

    # Pull any additional registered users from the database
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
                "password": password
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

#Saving cookie of user being logged in
credentials = User_Login()

authenticator = stauth.Authenticate(
    credentials,
    cookie_name="app_cookie",
    key="super_secret_key",
    cookie_expiry_days=30
)

#Login Page state initialization
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

# If user is logged in
if st.session_state.get("authentication_status"):
    #Loading assets
    with open("assets/Clean_Window.json","r",encoding="utf-8") as f:
        Clean_window=json.load(f)
    # Left to right Sidebar Gradient
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(to right, #2C325B, #2C325B10);
        }
        /* Optional: Ensure text color inside sidebar remains readable on dark gradients */
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
     # Main page content
     #Sidebar
    authenticator.logout("Logout", "sidebar")
    st.sidebar.write(f"Welcome, *{st.session_state['name']}*!")

    # Header
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="
            font-family: 'Orbitron',sans-serif;
            font-size: 5rem;
            white-space: nowrap; /* <-- Prevents the text from breaking into two lines */
            display: inline-block;
        ">
            Welcome to LinXray
        </h1>
    </div>
    """, unsafe_allow_html=True)
    st.space(30)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        target_url = st.text_input("Enter URL", placeholder="https://example.com", label_visibility="collapsed")
    
    st.space(40)
    
    # Custom colored and extended divider line
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

    # Scan Results
    st.space(30)
    st.markdown("""
        <div1 style="text-align: center;">
            <h2 style="
                font-family: monospace;
                white-space: nowrap;
                display: inline-block;
            ">
                Your Scan Results will Appear Here
            </h2>
        </div1>
        """, unsafe_allow_html=True)

# If login failed
elif st.session_state.get("authentication_status") is False:
    st.error("Username/password is incorrect")
    st.session_state["auth_mode"] = "Login"
    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
    authenticator.login(location="main", key="unique_login_form")
    st.markdown("---")
    if st.button("Need an account? Sign Up", use_container_width=True):
        st.session_state["auth_mode"] = "Sign Up"
        st.rerun()

# If user is not logged in yet (Status is None)
elif st.session_state.get("authentication_status") is None:
    
    # Show Login form ONLY when auth_mode is Login
    if st.session_state["auth_mode"] == "Login":
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        authenticator.login(location="main", key="unique_login_form")
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