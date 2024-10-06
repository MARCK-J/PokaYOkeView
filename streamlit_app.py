import streamlit as st
import pandas as pd
import math
from pathlib import Path
import requests
import time

# ------------------------------------------------------------------------
# Set up constants

TIME_DIFFERENCE = 5  # Time difference in seconds
ENTRIES_PER_READING = 20  # Number of entries per reading

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Temperature Dashboard',
    page_icon=':thermometer:',  # This is an emoji shortcode. Could be a URL too.
)

# ------------------------------------------------------------------------
# Set up the endpoint URL
endpoint_url = "http://192.168.0.17:80/getReadings"

# ------------------------------------------------------------------------
# Function to get data from the endpoint
def get_temperature_data():
    try:
        response = requests.get(endpoint_url)
        
        response.raise_for_status()  # Check for HTTP errors
        response_data = [float(reading) for reading in response.content.decode('utf-8').split(',')]
        #print("response: ", response_data) # Debugging
        return response_data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

# ------------------------------------------------------------------------
# Draw the page with real-time data updates

st.title(":thermometer: Real-time Temperature Dashboard")

# Create a container to display the chart
chart_placeholder = st.empty()
# Create a container to display the latest readings
latest_reading_placeholder = st.empty()

# Initialize an empty DataFrame to store the temperature readings
temperature_df = pd.DataFrame(columns=['Time', 'Temperature'])

# Loop to update the dashboard in real-time
while True:
    # Get temperature data from the endpoint
    readings = get_temperature_data()

    if readings:
        # Get the current time and create a list of times spaced by TIME_DIFFERENCE
        current_time = pd.Timestamp.now()
        time_list = [current_time - pd.Timedelta(seconds=i*TIME_DIFFERENCE) for i in range(len(readings))]
        temperature_data = {'Time': time_list, 'Temperature': readings}
        
        # Append the new data to the DataFrame
        new_df = pd.DataFrame(temperature_data)
        # temperature_df = pd.concat([temperature_df, new_df], ignore_index=True) Dado que se está recuperando una serie de datos, concatener está resultando en valores sobrepuestos
        temperature_df = new_df
        #print(temperature_df) # Debugging
        # Update the chart
        chart_placeholder.line_chart(
            temperature_df.set_index('Time'),
            y=['Temperature'],
            use_container_width=True
        )

        # Display the latest temperature readings
        latest_reading_placeholder.write(f"Latest temperature: {readings[0]:.2f}°C")

    # Wait for some seconds before fetching new data
    time.sleep(TIME_DIFFERENCE)
