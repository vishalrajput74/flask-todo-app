
from flask import Blueprint, request, jsonify, session
from app.models import User
# from app import db
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
# from flask_wtf.csrf import CSRFProtect
from app.extensions import csrf
from app.extensions import db 
from app.utils.decorators import api_login_required
api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api')

@api_auth_bp.route('/login', methods=['POST'])
@csrf.exempt
def api_login():
    # print("LOGIN API HIT")
    # print("Headers:", dict(request.headers))
    data = request.get_json(silent=True)
    # print("DATA RECEIVED:", data)
    if not data:
        # print("JSON missing or invalid")
        return jsonify({
            "error": "Invalid JSON or missing Content-Type: application/json"}), 400
        
    # print("Username:", data.get('username'))
    # print("Password:", data.get('password'))
    user = User.query.filter_by(username=data['username']).first()
    # print("User found:", user)
    if user and check_password_hash(user.password, data['password']):
        # print("Login success")
        session['user_id'] = user.id
        return jsonify({"message": "Login success", "user_id": user.id})
    # print("Invalid credentials")
    return jsonify({"message": "Invalid credentials"}), 401


@api_auth_bp.route('/register', methods=['POST'])
def api_register():
    # print("register route hit")
    data = request.get_json(silent=True)
    print("Data recive",data)

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    existing_user = User.query.filter_by(username=data['username']).first()
    # print("Existing User",existing_user)
    if existing_user:
        
        return jsonify({"error": "User already exists"}), 400
    
    hashed_password = generate_password_hash(data['password'])
    # print("Hshed pass",hashed_password)
    new_user = User(
        username=data['username'],
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()
    # print("create new user",new_user.id)
    return jsonify({"message": "User registered successfully"})

@api_auth_bp.route('/logout', methods=['POST'])
@csrf.exempt
@api_login_required
def api_logout():

    # print(" LOGOUT API HIT")
    # print("USER BEFORE:", session.get('user_id'))

    session.pop('user_id', None)

    # print("USER AFTER:", session.get('user_id'))

    return jsonify({"message": "Logged out successfully"})