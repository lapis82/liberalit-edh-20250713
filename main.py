import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# GitHub CSV URL
CSV_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/liberalita_edh.csv"

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    # Fallback for missing 'G' entries (lines 30 and 68)
    if pd.isna(df.loc[29, 'G']):
        df.loc[29, 'G'] = df.loc[29, 'F']
    if pd.isna(df.loc[67, 'G']):
        df.loc[67, 'G'] = df.loc[67, 'F']
    return df

# Parse coordinates from 'G' column
def extract_coordinates(loc_str):
    try:
        lat, lon = map(float, loc_str.strip("()").split(","))
        return lat, lon
    except:
        return None, None

# Main app
st.title("📜 Liberalitas Inscriptions Map")

df = load_data()
map_center = (41.9, 12.5)  # Rome center fallback

m = folium.Map(location=map_center, zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

# Loop through the DataFrame
for idx, row in df.iterrows():
    loc_str = row['G']
    transcription = row['B']

    lat, lon = extract_coordinates(loc_str)
    if lat is None or lon is None:
        continue

    popup_text = f"<strong>Transcription:</strong><br>{transcription}"
    folium.Marker(location=(lat, lon), popup=popup_text).add_to(marker_cluster)

# Display map
st_folium(m, width=700, height=500)
