import streamlit as st
import pandas as pd
import pydeck as pdk

# Set up the app
st.set_page_config(layout="wide", page_title="User Activity Map")
st.title("User Activity Map")

# 1. Data Loading with Validation
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('map.xlsx')
        
        # Coordinate extraction with validation
        coords = df['Custom parameter'].str.extract(r'([\d\.]+)[,\s]+([\d\.]+)')
        df['lat'] = pd.to_numeric(coords[0], errors='coerce')
        df['lon'] = pd.to_numeric(coords[1], errors='coerce')
        
        # Convert numerical columns and fill NA
        df['Event count'] = pd.to_numeric(df['Event count'], errors='coerce').fillna(1)
        df['Total users'] = pd.to_numeric(df['Total users'], errors='coerce').fillna(1)
        
        # Remove invalid coordinates
        return df.dropna(subset=['lat', 'lon'])
    
    except Exception as e:
        st.error(f"Data loading error: {str(e)}")
        return pd.DataFrame()

df = load_data()

# 2. Debug Info (show raw data if empty)
if df.empty:
    st.warning("No valid data found! Check your Excel file.")
    st.write("Required columns: 'Custom parameter' (with lat,lon), 'Event count', 'Total users'")
    st.stop()

# 3. Map Visualization with fixed parameters
try:
    # Fixed parameters
    size = 15  # Fixed point size
    color = "#FFA500"  # Fixed orange color
    
    # Convert color hex to RGB
    rgb = [int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    
    # Set viewport over Ethiopia
    view = pdk.ViewState(
        latitude=9.145,
        longitude=40.4897,
        zoom=5.5,
        pitch=0
    )
    
    # Calculate radius
    df['radius'] = pd.to_numeric(df['Event count']) * size / 5
    
    # Create visible points
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=['lon', 'lat'],
        get_radius='radius',
        get_fill_color=rgb + [200],  # Add transparency
        pickable=True,
        stroked=True,
        get_line_color=[0, 0, 0],
        line_width_min_pixels=1
    )
    
    # Tooltip template
    tooltip_html = """
    <b>{Location}</b><br>
    <span style='color:%s'>⬤</span> Users: {Total users}<br>
    Events: {Event count}
    """ % color
    
    # Render the map
    st.pydeck_chart(pdk.Deck(
        initial_view_state=view,
        layers=[layer],
        tooltip={
            "html": tooltip_html,
            "style": {"backgroundColor": "#333333", "color": "white"}
        },
        map_style="road"
    ))

except Exception as e:
    st.error(f"Map rendering failed: {str(e)}")
    st.info("Debug Data Preview:")
    st.dataframe(df[['Location', 'lat', 'lon', 'Event count', 'Total users']])