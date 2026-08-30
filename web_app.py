import pickle
import pandas as pd
import streamlit as st

import auth

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Laptop Price Predictor", page_icon="💻", layout="centered")

# ---------------------------------------------------------------------------
# Load trained model + dropdown options (cached so it only loads once)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_model_and_options():
    with open("laptop_price_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("dropdown_values.pkl", "rb") as f:
        options = pickle.load(f)
    return model, options


model, options = load_model_and_options()
gpu_map = options["Gpu_map"]

# ---------------------------------------------------------------------------
# Session state: is the user logged in?
# ---------------------------------------------------------------------------
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None


def show_login_page():
    st.markdown("<h1 style='text-align:center;'>💻 Laptop Price Predictor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray;'>Log in to get started</p>", unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In", use_container_width=True):
            success, message = auth.verify_user(username, password)
            if success:
                st.session_state.logged_in_user = username.strip()
                st.rerun()
            else:
                st.error(message)

    with tab_signup:
        new_username = st.text_input("Choose a username", key="signup_username")
        new_password = st.text_input("Choose a password", type="password", key="signup_password")
        if st.button("Sign Up", use_container_width=True):
            success, message = auth.register_user(new_username, new_password)
            if success:
                st.success(message + " Please switch to the Log In tab.")
            else:
                st.error(message)


def show_predictor_page():
    # Sidebar: user info + logout
    with st.sidebar:
        st.markdown(f"**Logged in as:** {st.session_state.logged_in_user}")
        if st.button("Log Out"):
            st.session_state.logged_in_user = None
            st.rerun()

    st.markdown("<h1 style='text-align:center;'>💻 Laptop Price Predictor</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center;color:gray;'>Welcome, {st.session_state.logged_in_user} — "
        f"fill in the specs below for a price estimate</p>",
        unsafe_allow_html=True,
    )

    st.subheader("🏷 Brand & Type")
    col1, col2, col3 = st.columns(3)
    company = col1.selectbox("Company", options["Company"])
    typename = col2.selectbox("Type", options["TypeName"])
    os_ = col3.selectbox("Operating System", options["OpSys"])

    st.subheader("⚙ Performance")
    col1, col2 = st.columns(2)
    cpu = col1.selectbox("CPU Brand", options["Cpu_brand"])
    ram = col2.select_slider("RAM (GB)", options=[4, 8, 16, 32, 64], value=8)

    col1, col2 = st.columns(2)
    gpu_brand = col1.selectbox("GPU Brand", list(gpu_map.keys()))
    gpu_name = col2.selectbox("Graphics Card (Model)", gpu_map[gpu_brand])

    st.subheader("🖥 Display")
    col1, col2 = st.columns(2)
    inches = col1.slider("Screen Size (inches)", 11.6, 17.3, 15.6, 0.1)
    ppi = col2.slider("PPI (Sharpness)", 100, 220, 141)

    col1, col2 = st.columns(2)
    touchscreen = col1.checkbox("Touchscreen")
    ips = col2.checkbox("IPS Display")

    st.subheader("🗄 Storage & Build")
    col1, col2, col3 = st.columns(3)
    hdd = col1.selectbox("HDD (GB)", [0, 500, 1024, 2048])
    ssd = col2.selectbox("SSD (GB)", [128, 256, 512, 1024, 2048], index=1)
    weight = col3.slider("Weight (kg)", 1.0, 3.5, 1.8, 0.1)

    st.markdown("")
    if st.button("Predict Price", type="primary", use_container_width=True):
        input_df = pd.DataFrame([{
            "Company": company, "TypeName": typename, "Inches": inches, "Ram": ram,
            "Weight": weight, "Touchscreen": int(touchscreen), "IPS": int(ips),
            "PPI": ppi, "Cpu_brand": cpu, "HDD": hdd, "SSD": ssd,
            "Gpu_name": gpu_name, "OpSys": os_,
        }])
        predicted_price = model.predict(input_df)[0]
        st.markdown(
            f"<h2 style='text-align:center;color:#3B8ED0;'>Estimated Price: ₹ {predicted_price:,.0f}</h2>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
if st.session_state.logged_in_user is None:
    show_login_page()
else:
    show_predictor_page()
