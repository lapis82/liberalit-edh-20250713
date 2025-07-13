import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import html
import re  # for cleaning metadata from transcriptions

# 🔗 Replace with your actual raw CSV URL from GitHub
CSV_URL = "https://raw.githubusercontent.com/lapis82/liberalit-edh-20250713/refs/heads/main/liberalita_edh.csv"

# Load data from GitHub
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    coords_col = 'coordinates (lat,lng)'
    
    # Fallback handling for known missing rows
    if pd.isna(df.loc[29, coords_col]):
        df.loc[29, coords_col] = df.loc[29, coords_col]
    if pd.isna(df.loc[67, coords_col]):
        df.loc[67, coords_col] = df.loc[67, coords_col]
    
    return df

# Helper: parse coordinates
def extract_coordinates(loc_str):
    try:
        lat, lon = map(float, loc_str.strip().split(","))
        return lat, lon
    except:
        return None, None

# 🎯 App setup
st.set_page_config(page_title="Liberalitas Map", layout="wide")
st.title("📍 Inscriptions of *Liberalitas*")
st.markdown("Explore locations and transcriptions of Roman inscriptions mentioning *liberalitas*.")

# 📊 Load and filter data
df = load_data()

# Sidebar filter
all_regions = df['province / Italic region'].dropna().unique()
selected_region = st.sidebar.selectbox("🗺️ Filter by Region", ["All"] + sorted(all_regions.tolist()))

if selected_region != "All":
    df = df[df['province / Italic region'] == selected_region]

# 🌍 Create map
m = folium.Map(location=(41.9, 12.5), zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    coords = row['coordinates (lat,lng)']
    transcription_raw = str(row['transcription']).strip()
    province = row.get('province / Italic region', 'Unknown')
    findspot = row.get('modern find spot', 'Unknown')

    if pd.isna(coords):
        continue

    lat, lon = extract_coordinates(coords)
    if lat is None or lon is None:
        continue

    # ✂️ Clean transcription of EDCS metadata prefixes
    transcription_clean = re.sub(r"^(MAI:|HD\d{5,}|EDCS[\d: ]+)\s*", "", transcription_raw)

    # 📜 HTML popup
    popup_html = f"""
    <div style="width: 300px; max-height: 250px; overflow-y: auto; font-size: 13px;">
        <strong><u>Province:</u></strong> {html.escape(str(province))}<br>
        <strong><u>Modern Findspot:</u></strong> {html.escape(str(findspot))}<br><br>
        <strong>Transcription:</strong><br>
        <pre style="white-space: pre-wrap;">{html.escape(transcription_clean)}</pre>
    </div>
    """
    folium.Marker(
        location=(lat, lon),
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(marker_cluster)

# 🗺️ Display map
st_folium(m, width=900, height=600)
