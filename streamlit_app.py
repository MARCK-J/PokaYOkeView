import streamlit as st
import pandas as pd
from pathlib import Path
import requests
import time

page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-color: #b9ffac;
    opacity: 0.8;
    background: repeating-linear-gradient(45deg, #a4ff93, #a4ff93 10px, #a4ff93 10px, #a4ff93 20px);
}
[data-testid="stMarkdownContainer"] * {
    color: #777777;  /* Soft gray font color */
}
[data-testid="stTextInputRootElement"] * {
    background-color: #e2ffdd;  /* Black font color */
    color:rgb(0, 0, 0);
}
[data-testid="stBaseButton-secondary"] {
    background-color: #e2ffdd;  /* Black font color */
}
</style>
'''

# ------------------------------------------------------------------------
# Set up constants

TIME_DIFFERENCE = 5  # Time difference in seconds
ENTRIES_PER_READING = 20  # Number of entries per reading

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Temperature Dashboard',
    page_icon='https://static.vecteezy.com/system/resources/previews/014/784/934/original/thermometer-tool-in-celsius-or-fahrenheit-with-leaf-green-silhouette-icon-temperature-measurement-instrument-eco-care-glyph-pictogram-bio-climate-control-degree-icon-isolated-illustration-vector.jpg',  # This is an emoji shortcode. Could be a URL too.
)

# ------------------------------------------------------------------------
# Set up the endpoint URLs
readings_endpoint = "http://192.168.0.17:80/getReadings"
limits_endpoint = "http://192.168.0.17:80/getLimits"
set_limits_endpoint = "http://192.168.0.17:80/setLimits"

# ------------------------------------------------------------------------
# Function to get temperature readings from the endpoint
def get_temperature_data():
    try:
        response = requests.get(readings_endpoint)
        response.raise_for_status()  # Check for HTTP errors
        response_data = [float(reading) for reading in response.content.decode('utf-8').split(',')]
        #print("response: ", response_data) # Debugging
        return response_data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching temperature data: {e}")
        return []

# Function to get temperature limits from the endpoint
def get_temperature_limits():
    try:
        response = requests.get(limits_endpoint)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()  # Parse the response as JSON
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching limits: {e}")
        return {"LowerTemperatureLimit": None, "HigherTemperatureLimit": None}
    
# Function to set new temperature limits
def set_temperature_limits(lower_limit, upper_limit):
    try:
        params = {'lower': lower_limit, 'higher': upper_limit}
        response = requests.post(set_limits_endpoint, params=params)
        response.raise_for_status()
        st.success(f"Temperature limits updated successfully to {lower_limit}°C (Lower) and {upper_limit}°C (Higher).")
    except requests.exceptions.RequestException as e:
        st.error(f"Error setting temperature limits: {e}")
        
# ------------------------------------------------------------------------
# Draw the page with real-time data updates
st.markdown(page_bg_img, unsafe_allow_html=True)

st.title(":thermometer: Real-time Temperature Dashboard")

# Create a container to display the chart
chart_placeholder = st.empty()
# Create a container to display the latest readings
latest_reading_placeholder = st.empty()

# Initialize an empty DataFrame to store the temperature readings
temperature_df = pd.DataFrame(columns=['Time', 'Temperature'])

# Get the initial temperature limits
limits = get_temperature_limits()

# Display the limits in text fields (initial values are populated from the endpoint)
lower_limit = st.text_input('Lower Temperature Limit (°C)', value=limits['LowerTemperatureLimit'])
upper_limit = st.text_input('Higher Temperature Limit (°C)', value=limits['HigherTemperatureLimit'])

# Add a button to submit the new limits
if st.button('Set Temperature Limits'):
    # Ensure the input values are valid numbers before sending them to the API
    try:
        lower_limit_value = float(lower_limit)
        upper_limit_value = float(upper_limit)
        set_temperature_limits(lower_limit_value, upper_limit_value)  # Call function to set new limits
    except ValueError:
        st.error("Please enter valid numerical values for the temperature limits.")

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
        temperature_df = new_df

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