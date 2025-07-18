import json
import random

from database import (
    add_item,
    create_session,
    get_balance,
    get_user,
    init_db,
    update_balance,
    validate_login,
    validate_session,
)
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__, static_folder="static", template_folder="templates")

SPIN_COST = 20
ITEMS = ["diamond", "gold_ingot", "iron_ingot", "emerald"]
PROBABILITIES = [0.1, 0.3, 0.4, 0.2]

ITEM_META = {
    "diamond": {"label": "Diamond", "color": "#3b82f6"},
    "gold_ingot": {"label": "Gold", "color": "#eab308"},
    "iron_ingot": {"label": "Iron", "color": "#9ca3af"},
    "emerald": {"label": "Emerald", "color": "#10b981"},
}


def extract_session_token(data=None):
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(None, 1)[1].strip()
    if data is None:
        data = request.get_json(silent=True) or {}
    return data.get("session_token")


@app.route("/casino/login", methods=["GET"])
def casino_login_page():
    return render_template("casino_login.html")


@app.route("/casino/spin", methods=["GET"])
def casino_spin_page():
    items_payload = [
        {
            "key": it,
            "label": ITEM_META[it]["label"],
            "color": ITEM_META[it]["color"],
        }
        for it in ITEMS
    ]
    return render_template(
        "casino_spin.html",
        spin_cost=SPIN_COST,
        items_json=json.dumps(items_payload),
    )


@app.route("/casino/api/login", methods=["POST"])
def casino_api_login():
    data = request.get_json(silent=True) or {}
    login_code = data.get("login_code")
    if not login_code:
        return jsonify({"error": "Missing login code"}), 400

    user = validate_login(login_code)
    if not user:
        return jsonify({"error": "Invalid login code"}), 401

    session_token = create_session(user["id"])
    return jsonify(
        {
            "message": "Login successful",
            "coin_balance": user["coin_balance"],
            "mc_nickname": user["mc_nickname"],
            "session_token": session_token,
        }
    )


@app.route("/casino/api/me", methods=["GET"])
def casino_api_me():
    token = extract_session_token()
    if not token:
        return jsonify({"error": "Missing session token"}), 401
    user_id = validate_session(token)
    if not user_id:
        return jsonify({"error": "Invalid or unauthorized session"}), 401
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(
        {
            "mc_nickname": user["mc_nickname"],
            "coin_balance": user["coin_balance"],
            "user_id": user["id"],
        }
    )


@app.route("/casino/api/spin", methods=["POST"])
def casino_api_spin():
    data = request.get_json(silent=True) or {}
    session_token = extract_session_token(data)
    if not session_token:
        return jsonify({"error": "Missing session token"}), 401
    user_id = validate_session(session_token)
    if not user_id:
        return jsonify({"error": "Invalid or unauthorized session"}), 401

    user = get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user["coin_balance"] < SPIN_COST:
        return (
            jsonify(
                {"error": "Not enough coins", "coin_balance": user["coin_balance"]}
            ),
            400,
        )

    update_balance(user_id, -SPIN_COST)
    result = random.choices(ITEMS, weights=PROBABILITIES, k=1)[0]
    add_item(user_id, result, 1)
    new_balance = get_balance(user_id)

    return jsonify({"result": result, "coin_balance": new_balance})


@app.route("/")
def root_redirect():
    return redirect(url_for("casino_login_page"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
