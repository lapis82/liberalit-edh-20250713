import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk # Added missing import for pydeck

# --- Page Configuration ---
st.set_page_config(page_title="Liberalitas Inscriptions Map", layout="wide")
st.title("📍 Map of Inscriptions Mentioning 'Liberalitas'")
st.markdown("This application displays the geographical locations of ancient inscriptions containing the word 'liberalitas'. Hover over a point on the map to see the transcription.")

# --- Sidebar for User Input ---
st.sidebar.header("Data Source")
st.sidebar.markdown("""
Enter the **raw** URL of your CSV file from GitHub.
To get the raw URL:
1. Navigate to your file on GitHub.
2. Click the "Raw" button.
3. Copy the URL from your browser's address bar.
""")

# Text input for the GitHub URL with a default value
default_url = "https://raw.githubusercontent.com/SatoruNakagawa/liberalitas/main/liberalita_edh.csv"
github_url = st.sidebar.text_input("GitHub Raw CSV URL:", default_url)


# --- Data Loading and Processing ---
# Use st.cache_data to cache the data and prevent reloading on every interaction.
@st.cache_data
def load_data(url):
    """
    Loads data from a GitHub raw URL, handles specific data corrections,
    and processes coordinates.
    """
    if not url:
        return pd.DataFrame() # Return empty dataframe if no URL is provided
    try:
        # Load the CSV file from the provided URL
        df = pd.read_csv(url)

        # --- Data Correction as per user request ---
        # For line 30 (index 29) and line 68 (index 67), if column 'G' is empty,
        # use the value from column 'F'.
        # We check for NaN (Not a Number) which is how pandas represents empty cells.
        if 29 < len(df) and pd.isna(df.loc[29, 'G']):
            df.loc[29, 'G'] = df.loc[29, 'F']
        if 67 < len(df) and pd.isna(df.loc[67, 'G']):
            df.loc[67, 'G'] = df.loc[67, 'F']

        # --- Coordinate Parsing ---
        # Create 'lat' and 'lon' columns.
        # We'll remove rows where coordinates are still missing or malformed.
        df.dropna(subset=['G'], inplace=True)

        # Define a function to safely parse coordinates
        def parse_coords(coord_str):
            try:
                # Split the string by comma and convert to float
                # Also strip any whitespace
                lat, lon = map(float, str(coord_str).strip().split(','))
                return lat, lon
            except (ValueError, AttributeError):
                # Return None if parsing fails
                return None, None

        # Apply the parsing function
        coords = df['G'].apply(lambda x: pd.Series(parse_coords(x)))
        coords.columns = ['lat', 'lon']

        # Join the new lat/lon columns back to the original dataframe
        df = pd.concat([df, coords], axis=1)

        # Remove any rows where coordinate parsing failed
        df.dropna(subset=['lat', 'lon'], inplace=True)
        
        # Ensure transcription column 'B' is treated as a string
        df['B'] = df['B'].astype(str)

        return df

    except Exception as e:
        # Display an error message if the data cannot be loaded or processed
        st.error(f"An error occurred while loading or processing the data: {e}")
        st.warning("Please ensure the URL is correct and points to a raw CSV file.")
        return pd.DataFrame() # Return an empty DataFrame on error

# --- Main App Logic ---

if github_url:
    data = load_data(github_url)

    if not data.empty:
        st.subheader("Interactive Inscription Map")

        # --- Map Display using PyDeck ---
        # Set the initial view state for the map (centered on Italy)
        view_state = pdk.ViewState(
            latitude=data['lat'].mean(),
            longitude=data['lon'].mean(),
            zoom=4,
            pitch=50,
        )

        # Define the layer for the map
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',  # Red color for points
            get_radius=15000,              # Radius of points in meters
            pickable=True                  # Allow hovering to pick points
        )

        # Define the tooltip
        tooltip = {
            "html": "<b>Transcription:</b><br/> {B} <br/><br/> <b>Location:</b> {G}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "font-family": "sans-serif",
                "font-size": "12px",
                "border-radius": "5px",
                "padding": "5px"
            }
        }

        # Create and render the map
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        ))

        # --- Data Table Display ---
        st.subheader("Inscription Data")
        st.markdown("Here is the raw data used for the map.")
        # Display relevant columns of the dataframe
        st.dataframe(data[['B', 'F', 'G', 'lat', 'lon']])

    else:
        st.info("Waiting for data to be loaded. Please check the URL in the sidebar.")
else:
    st.info("Please enter a GitHub URL in the sidebar to load the data.")

