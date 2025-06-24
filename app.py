from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
import random
import string
import hashlib
import requests

app = Flask(__name__)
CORS(app)  # This was missing in your merged app!

# ========== FRONTEND ROUTES ==========
@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/strength-checker')
def strength_checker():
    return render_template('strength.html')

@app.route('/random-generator')
def random_generator():
    return render_template('generator.html')

@app.route('/have-i-been-pawned')
def have_i_been_pawned():
    return render_template('pawn.html')

# ========== BACKEND LOGIC ROUTES ==========

# 🔒 Password Strength Checker Logic (from your working strength.py)
def check_password_strength(password):
    if len(password) < 8:
        return "Need at least 8 characters", "red"
    if not re.search(r"[A-Z]", password):
        return "Add uppercase letter", "orange"
    if not re.search(r"[a-z]", password):
        return "Add lowercase letter", "orange"
    if not re.search(r"\d", password):
        return "Add a number", "orange"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Add special character", "orange"
    return "Strong password!", "green"

# Password strength checker route
@app.route("/check-password-strength", methods=["POST"])
def check_password_strength_route():
    password = request.get_json().get("password", "")
    message, color = check_password_strength(password)
    return jsonify({"message": message, "color": color})

# 🔁 Random Password Generator Logic (from your working rando.py)
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

@app.route("/generate-password")
def generate():
    password = generate_password()
    return jsonify({"password": password})

# 🕵️‍♂️ Have I Been Pwned Logic (EXACT copy from your working pawn.py)
def check_pwned_password(password):
    # Hash the password with SHA-1
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    # Send request to Have I Been Pwned API using only the prefix
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "API Error"}, 500

    # Check if the suffix is in the list of returned hashes
    hashes = response.text.splitlines()
    for line in hashes:
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return {"breached": True, "count": int(count)}

    return {"breached": False, "count": 0}

# Breach checker route - using the EXACT same route as your working pawn.py
@app.route('/check-password', methods=['POST'])
def check_password():
    data = request.get_json()
    password = data.get('password', '')
    result = check_pwned_password(password)
    return jsonify(result)

# Fixed the syntax error
if __name__ == '__main__':
    app.run(debug=True)