import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FS_CLIENT_ID = os.environ.get("FS_CLIENT_ID")
FS_CLIENT_SECRET = os.environ.get("FS_CLIENT_SECRET")

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/api/fatsecret/today', methods=['GET'])
def get_fatsecret_data():
    if not FS_CLIENT_ID or not FS_CLIENT_SECRET:
        return jsonify({'error': 'FatSecret keys missing in environment'}), 400

    try:
        from fatsecret import Fatsecret
        fs = Fatsecret(FS_CLIENT_ID, FS_CLIENT_SECRET)
        
        # Запрос к FatSecret API
        # Обрати внимание: для доступа к личному дневнику конкретного профиля
        # требуется привязка OAuth_token пользователя.
        food_entries = fs.food_entries_get()

        total_calories = 0
        carbs = 0
        protein = 0
        fat = 0

        if food_entries:
            if isinstance(food_entries, dict):
                food_entries = [food_entries]
                
            for entry in food_entries:
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