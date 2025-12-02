import streamlit as st
import requests
from streamlit_option_menu import option_menu
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"


# =====================================================
# GLOBAL PAGE CONFIG + DARK THEME CSS
# =====================================================
st.set_page_config(page_title="Crop Insurance System", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #111827 !important;
            color: white;
        }
        .stApp {
            background-color: #111827 !important;
        }
        /* Cards */
        .policy-card {
            background-color: #1f2937;
            color: #f9fafb;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid #374151;
        }
        .policy-title {
            font-size: 22px;
            font-weight: 700;
        }
        .policy-label {
            font-weight: 600;
            color: #9ca3af;
        }
        /* Buttons */
        .stButton>button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            border: none;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #1e40af;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# CLAIM TIMELINE UI
# =====================================================
def claim_timeline_ui(claim):
    st.subheader("📌 Claim Status Timeline")

    steps = [
        ("pending", "🟡 Claim Submitted"),
        ("under_review", "🔵 Under Review"),
        ("approved", "🟢 Approved"),
        ("rejected", "🔴 Rejected"),
    ]

    st.markdown("""
        <style>
            .timeline-box {
                padding: 12px;
                background: #1f2937;
                border-radius: 10px;
                border: 1px solid #374151;
                margin-bottom: 10px;
            }
            .timeline-active {
                border-left: 6px solid #10b981;
                background: #064e3b;
            }
            .timeline-pending {
                opacity: 0.5;
            }
        </style>
    """, unsafe_allow_html=True)

    if claim.get("image_path"):
        st.image(claim["image_path"], width=300)

    if claim.get("model_result"):
        r = claim["model_result"]
        st.info(f"Prediction: **{r.get('label')}** ({r.get('confidence')}%)")

    for key, label in steps:
        if claim["status"] == key:
            st.markdown(f"<div class='timeline-box timeline-active'>{label}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='timeline-box timeline-pending'>{label}</div>", unsafe_allow_html=True)


# =====================================================
# LOGIN PAGE
# =====================================================
def login_screen():
    st.title("🌾 Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        if res.status_code == 200:
            st.session_state["token"] = res.json()["access_token"]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password")


# =====================================================
# SIGNUP PAGE
# =====================================================
def signup_screen():
    st.title("🧑‍🌾 Farmer Registration")

    name = st.text_input("Full Name", key="signup_name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_pass")

    if st.button("Create Account"):
        res = requests.post(f"{BASE_URL}/auth/signup", json={"name": name, "email": email, "password": password})
        if res.status_code == 200:
            st.success("Account created! Please login.")
        else:
            st.error(res.json()["detail"])


# =====================================================
# AVAILABLE POLICIES
# =====================================================
def available_policies():
    st.title("📃 Available Insurance Policies")

    res = requests.get(f"{BASE_URL}/policies/available")
    policies = res.json()

    if not policies:
        st.info("No policies available.")
        return

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    for p in policies:
        st.markdown(f"""
            <div class="policy-card">
                <div class="policy-title">{p["name"]}</div>
                <div class="policy-label">Crop:</div> {p["crop_type"]}<br><br>
                <div class="policy-label">Premium:</div> ₹{p["premium"]}<br>
            </div>
        """, unsafe_allow_html=True)

        if st.button(f"Buy {p['name']}", key=p["_id"]):
            pay = requests.post(
                f"{BASE_URL}/policies/buy?policy_id={p['_id']}",
                headers=headers
            )
            if pay.status_code == 200:
                st.success("Policy purchased successfully!")
            else:
                st.error("Error purchasing policy")


# =====================================================
# MY POLICIES
# =====================================================
def my_policies():
    st.title("📄 My Policies")

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    res = requests.get(f"{BASE_URL}/policies/", headers=headers)
    data = res.json()

    if not data:
        st.info("No purchased policies.")
        return

    for p in data:
        st.markdown(f"""
            <div class="policy-card">
                <div class="policy-title">{p["name"]}</div>
                <div class="policy-label">Premium:</div> ₹{p["premium"]}<br>
                <div class="policy-label">Status:</div> {p["status"]}
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# FILE A CLAIM
# =====================================================
def file_claim():
    st.title("📤 File Claim")

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    res = requests.get(f"{BASE_URL}/policies/", headers=headers)
    policies = res.json()

    if not policies:
        st.warning("Buy a policy first.")
        return

    policy_names = {p["name"]: p["_id"] for p in policies}
    selected = st.selectbox("Select Policy", list(policy_names.keys()))

    desc = st.text_area("Describe the damage")
    image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    lat = st.number_input("Latitude", step=0.0001)
    lon = st.number_input("Longitude", step=0.0001)

    if st.button("Submit Claim"):
        if not image:
            st.error("Upload an image.")
            return

        files = {"file": (image.name, image, "image/jpeg")}
        data = {"policy_id": policy_names[selected], "description": desc, "latitude": lat, "longitude": lon}

        r = requests.post(f"{BASE_URL}/claims/", headers=headers, data=data, files=files)

        if r.status_code == 200:
            st.success("Claim filed successfully!")
            claim_timeline_ui(r.json())
        else:
            st.error("Failed to submit claim")


# =====================================================
# CLAIM STATUS
# =====================================================
def claim_status():
    st.title("📊 Claim Status")

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    claims = requests.get(f"{BASE_URL}/claims/mine", headers=headers).json()

    if not claims:
        st.info("No claims found.")
        return

    claim_list = {f"{c['_id']} ({c['status']})": c["_id"] for c in claims}
    selected = st.selectbox("Select Claim", list(claim_list.keys()))
    cid = claim_list[selected]

    claim = requests.get(f"{BASE_URL}/claims/{cid}", headers=headers).json()
    claim_timeline_ui(claim)


# =====================================================
# MAIN ROUTING
# =====================================================
if "token" not in st.session_state:
    menu = option_menu(
        "Crop Insurance",
        ["Login", "Signup"],
        icons=["box-arrow-in-right", "person-plus"],
        menu_icon="shield",
        default_index=0,
        orientation="vertical"
    )

    if menu == "Login":
        login_screen()
    else:
        signup_screen()

else:
    menu = option_menu(
        "Dashboard",
        ["Available Policies", "My Policies", "File Claim", "Claim Status", "Logout"],
        icons=["file-earmark", "folder-check", "camera", "clock", "x-circle"],
        menu_icon="grid-fill",
        default_index=0,
        orientation="vertical"
    )

    if menu == "Available Policies":
        available_policies()
    elif menu == "My Policies":
        my_policies()
    elif menu == "File Claim":
        file_claim()
    elif menu == "Claim Status":
        claim_status()
    elif menu == "Logout":
        del st.session_state["token"]
        st.rerun()
