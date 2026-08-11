import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Единая база данных за текущий день
health_data = {
    # Питание (из FatSecret)
    'consumedCalories': 0,
    'carbs': 0,
    'protein': 0,
    'fat': 0,
    
    # Активность и Здоровье (из Garmin)
    'activeCalories': 0,
    'restingCalories': 0,
    'steps': 0,
    'distanceKm': 0.0,
    'avgHeartRate': 0,
    'sleepHours': 0.0
}

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Health Dashboard Backend Ready"})

# Эндпоинт для дашборда
@app.route('/api/health/today', methods=['GET'])
def get_health_data():
    return jsonify(health_data)

# Эндпоинт для приема данных из iOS Shortcuts
@app.route('/api/health/update', methods=['POST'])
def update_health_data():
    global health_data
    data = request.get_json(silent=True) or {}
    
    health_data = {
        'consumedCalories': round(float(data.get('calories', 0))),
        'carbs': round(float(data.get('carbs', 0)), 1),
        'protein': round(float(data.get('protein', 0)), 1),
        'fat': round(float(data.get('fat', 0)), 1),
        'activeCalories': round(float(data.get('activeCalories', 0))),
        'restingCalories': round(float(data.get('restingCalories', 0))),
        'steps': int(data.get('steps', 0)),
        'distanceKm': round(float(data.get('distanceKm', 0)), 2),
        'avgHeartRate': int(data.get('avgHeartRate', 0)),
        'sleepHours': round(float(data.get('sleepHours', 0)), 1)
    }
    
    print("Received updated metrics from Apple Health:", health_data)
    return jsonify({"status": "success", "data": health_data})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)