from flask import Flask, request, jsonify
import random
from database import init_db, validate_login, update_balance, add_item, get_user, create_session, validate_session

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login_code = data.get('login_code')
    if not login_code:
        return jsonify({'error': 'Missing login code'}), 400
    user = validate_login(login_code)
    if user:
        # Create a session token
        session_token = create_session(user['id'])
        return jsonify({
            'message': 'Login successful',
            'user_id': user['id'],
            'coin_balance': user['coin_balance'],
            'mc_nickname': user['mc_nickname'],
            'session_token': session_token
        })
    return jsonify({'error': 'Invalid login code'}), 401

@app.route('/spin', methods=['POST'])
def spin():
    data = request.json
    user_id = data.get('user_id')
    session_token = data.get('session_token')

    spin_cost = 20
    items = ['diamond', 'gold_ingot', 'iron_ingot', 'emerald']
    probabilities = [0.1, 0.3, 0.4, 0.2]

    if not session_token or not validate_session(session_token, user_id):
        return jsonify({'error': 'Invalid or unauthorized session'}), 401

    user = get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user['coin_balance'] < spin_cost:
        return jsonify({'error': 'Not enough coins'}), 400
    update_balance(user_id, -spin_cost)

    result = random.choices(items, weights=probabilities, k=1)[0]
    add_item(user_id, result, 1)
    return jsonify({'result': result})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)