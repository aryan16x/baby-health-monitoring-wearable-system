from flask import Flask, request, jsonify

app = Flask(__name__)

# Route to handle data coming from ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    # Parse data from POST request
    temperature = request.form.get('temperature')
    humidity = request.form.get('humidity')

    if not temperature or not humidity:
        return jsonify({"status": "error", "message": "Invalid data received"}), 400

    # Log received data (for now, just print to console)
    print(f"Received data - Temperature: {temperature}°C, Humidity: {humidity}%")

    # You can add further processing or data storage here, e.g., saving to a database
    # For example: save_data_to_database(temperature, humidity)

    # Return a success response to ESP32
    return jsonify({"status": "success", "message": "Data received successfully"})

# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
