from flask import Flask, request, jsonify

app = Flask(__name__)

# Global variable to store the latest sensor data
sensor_data = {
    "temperature": 37.5,
    "humidity": 60.0,
    "heartRate": 73,
    "fallDetected": False,
    "cryDetected": False,
    "sleepStage": 1
}

# Route to handle data coming from ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    # Parse data from POST request
    temperature = request.form.get('temperature')
    humidity = request.form.get('humidity')
    heartRate = request.form.get('heartRate')
    fallDetected = request.form.get('fallDetected')
    cryDetected = request.form.get('cryDetected')
    sleepStage = request.form.get('sleepStage')

    # Validate incoming data
    if None in (temperature, humidity, heartRate, fallDetected, cryDetected, sleepStage):
        return jsonify({"status": "error", "message": "Invalid data received"}), 400

    # Log received data (for now, just print to console)
    print(f"Received data - Temperature: {temperature}°C, Humidity: {humidity}%, Heart Rate: {heartRate} bpm, Fall Detected: {fallDetected}, Cry Detected: {cryDetected}, Sleep Stage: {sleepStage}")

    # Store the received data in the global variable
    sensor_data['temperature'] = temperature
    sensor_data['humidity'] = humidity
    sensor_data['heartRate'] = heartRate
    sensor_data['fallDetected'] = fallDetected
    sensor_data['cryDetected'] = cryDetected
    sensor_data['sleepStage'] = sleepStage

    # Return a success response to ESP32
    return jsonify({"status": "success", "message": "Data received successfully"})

# Route to fetch the latest sensor data
@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    return jsonify(sensor_data)

# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
