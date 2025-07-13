import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# CSV file on GitHub
CSV_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/liberalita_edh.csv"

# Load and preprocess
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)

    # Use fallback for missing coordinates if needed (lines 30, 68)
    coords_col = 'coordinates (lat,lng)'
    if pd.isna(df.loc[29, coords_col]):
        df.loc[29, coords_col] = df.loc[29, coords_col]
    if pd.isna(df.loc[67, coords_col]):
        df.loc[67, coords_col] = df.loc[67, coords_col]
    
    return df

# Coordinate parser
def extract_coordinates(loc_str):
    try:
        lat, lon = map(float, loc_str.strip().split(","))
        return lat, lon
    except:
        return None, None

# Load data
df = load_data()

# Sidebar filter
all_regions = df['province / Italic region'].dropna().unique()
selected_region = st.sidebar.selectbox("🗺️ Filter by Region", ["All"] + sorted(all_regions.tolist()))

if selected_region != "All":
    df = df[df['province / Italic region'] == selected_region]

# Map setup
st.title("📍 Inscriptions of Liberalitas")
st.markdown("Explore locations and transcriptions of Roman inscriptions mentioning *liberalitas*.")

m = folium.Map(location=(41.9, 12.5), zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

# Loop and add markers
for _, row in df.iterrows():
    coords = row['coordinates (lat,lng)']
    transcription = row['transcription']
    province = row.get('province / Italic region', 'Unknown')
    findspot = row.get('modern find spot', 'Unknown')

    if pd.isna(coords):
        continue

    lat, lon = extract_coordinates(coords)
    if lat is None or lon is None:
        continue

    # HTML popup
    popup_html = f"""
    <div style="width: 300px; max-height: 200px; overflow-y: auto; font-size: 13px;">
        <strong><u>Province:</u></strong> {province}<br>
        <strong><u>Modern Findspot:</u></strong> {findspot}<br><br>
        <strong>Transcription:</strong><br>{transcription}
    </div>
    """
    folium.Marker(location=(lat, lon),
                  popup=folium.Popup(popup_html, max_width=300)).add_to(marker_cluster)

# Display map
st_folium(m, width=800, height=600)
