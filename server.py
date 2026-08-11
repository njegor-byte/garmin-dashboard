import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FS_CLIENT_ID = os.environ.get("FS_CLIENT_ID")
FS_CLIENT_SECRET = os.environ.get("FS_CLIENT_SECRET")

def get_fatsecret_token():
    """Автоматическое получение fresh access_token через OAuth 2.0"""
    url = "https://oauth.fatsecret.com/connect/token"
    data = {'grant_type': 'client_credentials', 'scope': 'basic'}
    auth = (FS_CLIENT_ID, FS_CLIENT_SECRET)
    
    response = requests.post(url, data=data, auth=auth)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/api/fatsecret/today', methods=['GET'])
def get_fatsecret_data():
    if not FS_CLIENT_ID or not FS_CLIENT_SECRET:
        return jsonify({'error': 'FatSecret keys are missing'}), 400

    token = get_fatsecret_token()
    if not token:
        return jsonify({'error': 'Failed to obtain FatSecret access token'}), 500

    try:
        # Запрос данных дневника за сегодня через REST API
        url = "https://platform.fatsecret.com/rest/server.api"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "method": "food_entries.get.v2",
            "format": "json"
        }
        
        r = requests.get(url, headers=headers, params=params)
        data = r.json()

        total_calories = 0
        carbs = 0
        protein = 0
        fat = 0

        # Разбор ответа
        entries = data.get('food_entries', {}).get('food_entry', [])
        if isinstance(entries, dict):
            entries = [entries]

        for entry in entries:
            total_calories += float(entry.get('calories', 0))
            carbs += float(entry.get('carbohydrate', 0))
            protein += float(entry.get('protein', 0))
            fat += float(entry.get('fat', 0))

        return jsonify({
            'consumedCalories': round(total_calories),
            'carbs': round(carbs, 1),
            'protein': round(protein, 1),
            'fat': round(fat, 1)
        })

    except Exception as e:
        print(f"FatSecret Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)