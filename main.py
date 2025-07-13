import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# URL to your actual GitHub raw CSV
CSV_URL = "https://raw.githubusercontent.com/lapis82/liberalit-edh-20250713/refs/heads/main/liberalita_edh.csv"

# Load and preprocess the data
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    coords_col = 'coordinates (lat,lng)'
    
    # Fill known missing lines (30, 68) using fallback if available
    for i in [29, 67]:  # 0-indexed: line 30 = row 29
        if pd.isna(df.loc[i, coords_col]):
            df.loc[i, coords_col] = df.loc[i, coords_col]  # no alternative fallback needed now
    return df

# Parse coordinates safely
def extract_coordinates(loc_str):
    try:
        lat, lon = map(float, loc_str.strip().split(","))
        return lat, lon
    except:
        return None, None

# Streamlit app
st.title("📍 Inscriptions of Liberalitas")
st.markdown("Map of ancient Roman inscriptions mentioning *liberalitas*.")

df = load_data()
coords_col = 'coordinates (lat,lng)'
text_col = 'transcription'

m = folium.Map(location=(41.9, 12.5), zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    loc_str = row[coords_col]
    transcription = row[text_col]

    if pd.isna(loc_str):
        continue

    lat, lon = extract_coordinates(loc_str)
    if lat is None or lon is None:
        continue

    popup = f"<strong>Transcription:</strong><br>{transcription}"
    folium.Marker(location=(lat, lon), popup=popup).add_to(marker_cluster)

st_data = st_folium(m, width=700, height=500)
