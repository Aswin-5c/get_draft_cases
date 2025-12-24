import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# Configuration
API_URL = "http://localhost:8000"
st.set_page_config(page_title="Production Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

# Theme & Styling (Dark Mode forced via CSS injection if needed, but Streamlit respects system preference or config)
st.markdown("""
<style>
    .reportview-container {
        background: #000000;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background: #111111;
    }
</style>
""", unsafe_allow_html=True)

def fetch_clients():
    try:
        response = requests.get(f"{API_URL}/clients")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_analytics(client_id, start_date, end_date):
    try:
        params = {
            "client_id": client_id,
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d")
        }
        response = requests.get(f"{API_URL}/analytics", params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_overview(refresh=False):
    try:
        params = {"refresh": "true"} if refresh else {}
        response = requests.get(f"{API_URL}/overview", params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# ... (rest of the code)

# Initial State


# Sidebar
st.sidebar.title("Analytics Controls")

# Client Selection
clients = fetch_clients()
client_options = {c['client_name']: c['id'] for c in clients}

# Sidebar Navigation
if st.sidebar.button("Back to Overview"):
    st.query_params.clear()
    # Reset all relevant session state
    st.session_state.client_index = 0
    # Optional: Clear loaded data if you want a fresh start
    # for key in list(st.session_state.keys()):
    #     if key.startswith("data_"):
    #         del st.session_state[key]
    st.rerun()

# Initialize client index if not set
if 'client_index' not in st.session_state:
    st.session_state.client_index = 0

def on_client_change():
    # Update session state when selectbox changes
    pass

def set_selected_client(client_name):
    try:
        # Update both index and the selectbox key
        st.session_state.client_select = client_name
        # We also need to update the index to keep them in sync, though selectbox might handle it via key
        # But finding the index is safe
        options = [""] + list(client_options.keys())
        st.session_state.client_index = options.index(client_name)
    except ValueError:
        pass

selected_client_name = st.sidebar.selectbox(
    "Select Client", 
    options=[""] + list(client_options.keys()),
    index=st.session_state.client_index,
    key="client_select",
    on_change=on_client_change
)

# Update index in state if changed manually
if selected_client_name:
    options = [""] + list(client_options.keys())
    try:
        st.session_state.client_index = options.index(selected_client_name)
        
        # Add to Recently Viewed
        if 'recent_clients' not in st.session_state:
            st.session_state.recent_clients = []
            
        # Remove if exists (to move to top)
        if selected_client_name in st.session_state.recent_clients:
            st.session_state.recent_clients.remove(selected_client_name)
            
        # Add to front
        st.session_state.recent_clients.insert(0, selected_client_name)
        
        # Keep only last 5
        if len(st.session_state.recent_clients) > 5:
            st.session_state.recent_clients = st.session_state.recent_clients[:5]
            
    except ValueError:
        st.session_state.client_index = 0
else:
    st.session_state.client_index = 0

# Date Selection
today = date.today()
default_start = today
date_range = st.sidebar.date_input("Date Range", [default_start, today])

# Persistence Logic
import json
import os

FAVOURITES_FILE = "favourites.json"

def load_favourites():
    if os.path.exists(FAVOURITES_FILE):
        try:
            with open(FAVOURITES_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_favourites(favourites):
    try:
        with open(FAVOURITES_FILE, "w") as f:
            json.dump(favourites, f)
    except Exception as e:
        print(f"Error saving favourites: {e}")

# Initialize session state from file
if 'pinned_clients' not in st.session_state:
    st.session_state.pinned_clients = load_favourites()

# Favourite Button
if selected_client_name:
    # Ensure list exists in session state (redundant but safe)
    if 'pinned_clients' not in st.session_state:
        st.session_state.pinned_clients = load_favourites()
        
    is_pinned = selected_client_name in st.session_state.pinned_clients
    btn_label = "Remove from Favourites" if is_pinned else "Add to Favourites"
    
    if st.sidebar.button(btn_label):
        if is_pinned:
            st.session_state.pinned_clients.remove(selected_client_name)
        else:
            st.session_state.pinned_clients.append(selected_client_name)
        
        # Save to file immediately
        save_favourites(st.session_state.pinned_clients)
        st.rerun()

# Auto-Call API on Selection
if selected_client_name:
    if len(date_range) != 2:
        st.error("Please select a valid start and end date.")
    else:
        start_date, end_date = date_range
        if start_date > end_date:
            st.error("Start date must be earlier than end date.")
        else:
            client_id = client_options[selected_client_name]
            
            # Auto-fetch data
            with st.spinner("Fetching study data… Please wait."):
                data = fetch_analytics(client_id, start_date, end_date)
            
            if data is None:
                st.error("Unable to fetch data at the moment. Please try again later.")
            elif data['total_cases'] == 0:
                st.warning("No cases found for the selected client and date range.")
            else:
                # Main Dashboard
                st.title(f"Analytics for {selected_client_name}")
                
                # Layout: Metric + Chart side-by-side
                col_metric, col_chart = st.columns([1, 2])
                
                with col_metric:
                    st.metric("Draft Cases", data['draft_cases'])
                    
                with col_chart:
                    modality_data = data['modality_distribution']
                    if modality_data:
                        df = pd.DataFrame(list(modality_data.items()), columns=['Modality', 'Count'])
                        # Reverted to Bar Chart
                        fig = px.bar(df, x='Modality', y='Count', color='Modality', template="plotly_dark")
                        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No modality data available.")
                
                st.markdown("---")
                
                # Detailed Case List
                if data.get('cases'):
                    st.subheader("Draft Case Details")
                    df_cases = pd.DataFrame(data['cases'])
                    # Select and rename columns for display
                    display_cols = ['patient_name', 'patient_id', 'created_time', 'series_count', 'instance_count', 'modality', 'study_description']
                    df_display = df_cases[display_cols]
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.info("No detailed case info available.")

# Initial State
# Initial State
# Initial State / Dashboard Home
if not selected_client_name:
    st.title("Draft Cases Dashboard")
    
    # Initialize dashboard_counts if not present
    if 'dashboard_counts' not in st.session_state:
        st.session_state.dashboard_counts = {}

    # Auto-fetch counts for Favourite Clients
    if 'pinned_clients' in st.session_state and st.session_state.pinned_clients:
        # Check if we need to fetch (e.g., if counts are missing or stale)
        # For now, we'll fetch every time the dashboard loads to ensure fresh data
        # To avoid infinite rerun loops, we can check a flag or just do it once per render
        
        clients_to_fetch = st.session_state.pinned_clients
        today = date.today()
        
        # We use a placeholder to show loading status without blocking the whole UI if possible,
        # but for simplicity and correctness, we'll iterate and fetch.
        # To prevent excessive API calls on every interaction, we could cache this, 
        # but the user requested "whenever user is hitting the main dashboard call the api".
        
        # We need to be careful not to trigger a rerun inside the loop unless necessary.
        # Since we are just updating session_state, we don't need to rerun.
        
        for client_name in clients_to_fetch:
            # Only fetch if not already fetched in this session or if we want to force update
            # User said "whenever user is hitting the main dashboard", so we fetch.
            
            # Optimization: Check if we just fetched it (to avoid loop on rerun)
            # But Streamlit reruns the whole script. 
            # Let's just fetch.
            
            try:
                c_id = client_options.get(client_name)
                if c_id:
                    c_data = fetch_analytics(c_id, today, today)
                    if c_data:
                        st.session_state.dashboard_counts[client_name] = c_data['draft_cases']
                    else:
                        st.session_state.dashboard_counts[client_name] = "Err"
            except Exception:
                st.session_state.dashboard_counts[client_name] = "?"

    st.markdown("---")

    # 2. Favourite Clients Section
    st.subheader("Favourite Clients")
    
    if 'pinned_clients' not in st.session_state:
        st.session_state.pinned_clients = []
        
    if not st.session_state.pinned_clients:
        st.info("No favourite clients. Add a client to favourites from their analytics page.")
    else:
        # Display as rows with counts
        for client_name in st.session_state.pinned_clients:
            count = st.session_state.dashboard_counts.get(client_name, "-")
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{client_name}**")
            with col2:
                st.write(f"Drafts (Today): {count}")
            with col3:
                st.button("View", key=f"view_pin_{client_name}", on_click=set_selected_client, args=(client_name,))
