# streamlit_app.py
import streamlit as st
import requests
import time

# Set the title of the app and sidebar configuration
st.set_page_config(page_title='Baby Health Monitoring System', layout='wide')
st.title('Real-time Baby Health Monitoring System')

# Sidebar for configuration
st.sidebar.header('Settings')
refresh_rate = st.sidebar.slider('Refresh Rate (seconds)', 1, 10, 5)

# Function to fetch data from Flask
def fetch_data():
    try:
        response = requests.get('https://baby-health-monitoring-wearable-device.onrender.com/fetch-data')
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        data['heartRate'] = float(data['heartRate'])
        data['humidity'] = float(data['humidity'])
        data['sleepStage'] = int(data['sleepStage'])
        data['temperature'] = float(data['temperature'])
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to determine baby's mood based on sleep stage
def get_baby_mood(sleep_stage):
    mood_map = {
        0: '😴 Peaceful (Deep Sleep)',
        1: '😊 Relaxed (Light Sleep)',
        2: '🛌 Dreaming (REM Sleep)',
        3: '😄 Active (Awake)',
    }
    return mood_map.get(sleep_stage, '😐 Unknown Mood')

# Function to determine the color based on temperature
def get_temperature_color(temp):
    if temp < 36:
        return '#B7E0FF'  # Too cold
    elif 36 <= temp <= 37.5:
        return '#C0EBA6'  # Comfortable
    else:
        return '#FF8A8A'  # Too hot

# Function to show notifications for fall or cry detection
def show_notifications(fall_detected, cry_detected):
    if fall_detected == 'True':
        st.warning("⚠️ Fall Detected! Please check on the baby.")
    if cry_detected == 'True':
        st.warning("😭 Cry Detected! Baby needs attention.")

# Create a placeholder for sensor data
data_placeholder = st.empty()

# Streamlit app loop
while True:
    data = fetch_data()
    if data:
        # Clear the previous data and update with new data
        with data_placeholder.container():
            st.write("### Baby's Current Status")

            # Notifications for fall and cry detection
            show_notifications(data['fallDetected'], data['cryDetected'])

            # Temperature card with dynamic background color
            temp_color = get_temperature_color(data['temperature'])
            st.markdown(
                f"""
                <div style='background-color: {temp_color}; border-radius: 10px; padding: 10px;'>
                    <h4>Temperature</h4>
                    <p><strong>Current:</strong> {data['temperature']} °C</p>
                    <p><strong>Status:</strong> {"Good" if (data['temperature']<39 and data['temperature']>36) else "Uncomfortable"}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )

            # Humidity and Heart Rate (standard cards)
            st.write("### Sensor Readings")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"""
                    <div style='background-color: #C4D7FF;border: 2px solid #C4D7FF; border-radius: 10px; padding: 10px;'>
                        <h4>Humidity</h4>
                        <p><strong>Current:</strong> {data['humidity']} %</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    f"""
                    <div style='background-color: #FFCFB3; border: 2px solid #FFCFB3; border-radius: 10px; padding: 10px;'>
                        <h4>Heart Rate</h4>
                        <p><strong>Current:</strong> {data['heartRate']} bpm</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

            # Baby's mood based on sleep stage
            baby_mood = get_baby_mood(data['sleepStage'])
            st.markdown(
                f"""
                <div style='background-color: #E5D9F2; border: 2px solid #E5D9F2; border-radius: 10px; padding: 10px; margin-top: 10px;'>
                    <h4>Sleep Stage</h4>
                    <p><strong>Current Stage:</strong> {data['sleepStage']}</p>
                    <p><strong>Baby's Mood:</strong> {baby_mood}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )

    # Refresh every set interval
    time.sleep(refresh_rate)
