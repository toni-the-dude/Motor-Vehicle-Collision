import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
    "../Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used "
             "to analyze motor vehicle collisions in NYC")

@st.cache_data # Do not redo computations every time the app is rerun (unless the code is changed)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[["CRASH_DATE", "CRASH_TIME"]]) # Read nrows from DATA_URL and format date, time
    data.dropna(subset=["LATITUDE", "LONGITUDE"], inplace=True) # Drop missing values; they might break the map
    lowercase = lambda x: str(x).lower() # Concise function for lowercasing
    data.rename(lowercase, axis="columns", inplace=True) # Lowercase our column names
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True) # Rename a particularly long column name
    return data

data = load_data(100000)
original_data = data
# Map
st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19) # 19 turned out to be the max
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any")) # Showcase map with selected data
# Hourly
st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data["date/time"].dt.hour == hour] # Sort dataset by given hour

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data["latitude"]), np.average(data["longitude"])) # We want our map to zoom in on this point
# 3D map, first layer
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9", # Arbitrary style choice
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11, # Arbitrary
        "pitch": 50 # Arbitrary
    },
    layers=[
        pdk.Layer( # Second layer, related to the columns on the map
            "HexagonLayer", # Arbitrary shape
            data=data[["date/time", "latitude", "longitude"]], # Subset of data
            get_position=["longitude", "latitude"],
            radius=100, # Radius of the chosen shape
            extruded=True, # Turns our shape 3D
            pickable=True,
            elevation_scale=4, # Height multiplier
            elevation_range=[0, 1000], # Height range
        ),
    ],
))
# Histogram
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data["date/time"].dt.hour >= hour) & (data["date/time"].dt.hour < (hour + 1))
]
hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0, 60))[0] # Create histogram
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist}) # Create plot
fig = px.bar(chart_data, x="minute", y="crashes", hover_data=["minute", "crashes"], height=400) # Beautify plot
st.write(fig)

# Top 5
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people", ["Pedestrians", "Cyclists", "Motorists"])

if select == "Pedestrians":
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=["injured_pedestrians"], ascending= False).dropna(how="any")[:5]) # Query data for injured pedestrians to show the top 5 most dangerous streets for pedestrians

elif select == "Cyclists":
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=["injured_cyclists"], ascending= False).dropna(how="any")[:5]) # Query data for injured cyclists to show the top 5 most dangerous streets for cyclists

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=["injured_motorists"], ascending= False).dropna(how="any")[:5]) # Query data for injured motorists to show the top 5 most dangerous streets for motorists

# Raw
if st.checkbox("Show Raw Data", False): # Optionally look over raw data
    st.subheader('Raw Data')
    st.write(data)