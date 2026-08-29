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
    
    # DELETE THIS AFTER, ITS TEMP, PASS IS ATRE1DES
    credentials["usernames"]["test"] = {
        "name": "Test User",
        "password": "$2a$12$AegsROFAPWMvQgNVbLkRK.jYZa/ZWqk.vJFnWMqeVwQJMLBfkgBni"
    }

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
     # Main page content
     pass

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
        st.markdown("---")
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
                hashed_pw = stauth.Hasher([new_password]).generate()[0]
                if register_user_in_db(new_username, new_name, hashed_pw):
                    st.success("Account created! Switch back to Login to sign in.")
                else:
                    st.error("Username already exists or database error.")
                    
        st.markdown("---")
        if st.button("Already have an account? Login", use_container_width=True):
            st.session_state["auth_mode"] = "Login"
            st.rerun()