import streamlit as st
import requests

# --- Config & State ---
API_URL = "http://127.0.0.1:8000"

if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = 'Login'

# --- Custom Styling ---
st.markdown("""
    <style>
    .main-header {font-size: 3rem; color: #9B2226; font-weight: 800;}
    .sub-header {color: #AE2012;}
    .card {padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- Functions ---
def login_user(username, password):
    try:
        res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state['user'] = res.json()
            st.rerun()
        else:
            st.error("Invalid username or password")
    except:
        st.error("Backend is not running.")

def signup_user(username, password):
    try:
        res = requests.post(f"{API_URL}/signup", json={"username": username, "password": password})
        if res.status_code == 200:
            st.success("Account created! Please log in.")
            st.session_state['auth_mode'] = 'Login'
        else:
            st.error("Username already exists.")
    except:
        st.error("Backend error.")

# --- App Layout ---

# 1. Authentication View
if not st.session_state['user']:
    st.markdown("<h1 class='main-header'>PartyHost 🍷</h1>", unsafe_allow_html=True)
    st.markdown("### Never worry about who owes what.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150) # Party icon
        
    with col2:
        mode = st.radio("Select Mode", ["Login", "Sign Up"], horizontal=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if mode == "Login":
            if st.button("Sign In", type="primary"):
                login_user(username, password)
        else:
            if st.button("Create Account", type="primary"):
                signup_user(username, password)

# 2. Dashboard View (After Login)
else:
    user = st.session_state['user']
    
    # Sidebar
    with st.sidebar:
        st.title(f"Hello, {user['username']}!")
        if st.button("Logout"):
            st.session_state['user'] = None
            st.rerun()
    
    st.markdown("<h1 class='main-header'>Your Parties 🎉</h1>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["View Groups", "Create New Group"])

    # Tab 1: View Groups & Expenses
    with tab1:
        try:
            groups_res = requests.get(f"{API_URL}/groups/")
            groups = groups_res.json()
            
            if not groups:
                st.info("No groups found. Create one!")
                
            for group in groups:
                with st.expander(f"📂 {group['name']}"):
                    st.write("### Expenses")
                    total_spent = 0
                    if group['expenses']:
                        for exp in group['expenses']:
                            payer = exp.get('payer') or {}
                            payer_text = f"Paid by: {payer.get('username')}" if payer.get('username') else f"Paid by User ID: {exp['paid_by_id']}"
                            st.markdown(f"""
                            <div class='card'>
                                <b>{exp['description']}</b><br>
                                Amount: ₹{exp['amount']} <br>
                                <small>{payer_text}</small>
                            </div>
                            """, unsafe_allow_html=True)
                            total_spent += exp['amount']
                        st.metric("Total Group Spend", f"₹{total_spent}")
                    else:
                        st.write("No expenses yet.")

                    st.divider()
                    
                    # Add Expense to this group
                    with st.form(key=f"add_exp_{group['id']}"):
                        st.write("➕ Add Expense")
                        desc = st.text_input("Description")
                        amt = st.number_input("Amount", min_value=0.0)
                        if st.form_submit_button("Add"):
                            exp_data = {
                                "description": desc,
                                "amount": amt,
                                "paid_by_id": user['id'],
                                "group_id": group['id']
                            }
                            res = requests.post(f"{API_URL}/expenses/", json=exp_data)
                            if res.status_code == 200:
                                st.success("Expense added!")
                                st.rerun()
        except Exception as e:
            st.error(f"Connection error: {e}")

    # Tab 2: Create Group
    with tab2:
        st.subheader("Start a new party ledger")
        with st.form("new_group"):
            grp_name = st.text_input("Group Name (e.g., 'Goa Trip')")
            if st.form_submit_button("Create Group"):
                g_data = {"name": grp_name, "created_by": user['id']}
                res = requests.post(f"{API_URL}/groups/", json=g_data)
                if res.status_code == 200:
                    st.success(f"Group '{grp_name}' created!")
                    st.rerun()