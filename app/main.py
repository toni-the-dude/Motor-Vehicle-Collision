import streamlit as st
import pandas as pd
import numpy as np

DATA_URL = (
    "../Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used "
             "to analyze motor vehicle collisions in NYC")

@st.cache(persist=True) # Do not redo computations every time the app is rerun (unless the code is changed)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[["CRASH_DATE", "CRASH_TIME"]]) # Read nrows from DATA_URL and format date, time
    data.dropna(subset=["LATITUDE", "LONGITUDE"], inplace=True) # Drop missing values; they might break the map
    lowercase = lambda x: str(x).lower() # Concise function for lowercasing
    data.rename(lowercase, axis="columns", inplace=True) # Lowercase our column names
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True) # Rename a particularly long column name
    return data

data = load_data(100000)

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19) # 19 turned out to be the max
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any")) # Showcase map with selected data

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data["date/time"].dt.hour == hour]




if st.checkbox("Show Raw Data", False): # Optionally look over raw data
    st.subheader('Raw Data')
    st.write(data)