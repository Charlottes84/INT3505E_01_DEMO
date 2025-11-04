from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt,
    JWTManager
)

from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
from datetime import timedelta

import requests
import os 

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join("gateway.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
app.config["JWT_SECRET_KEY"] = "mot-secret-key-khong-duoc-ghi-o-day"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None 

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if "admin" not in claims.get("roles", []):
                return {"message": "Authorization Error: Admin access required"}, 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

AUTH_SERVICE_URL = "http://127.0.0.1:5001"
BOOK_SERVICE_URL = "http://127.0.0.1:5002"

def forward_request(service_url, endpoint):
    url = f"{service_url}{endpoint}"

    params = request.args
    data = request.get_data()
    headers = {key: value for (key, value) in request.headers if key != 'Host'}

    try:
        res = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=data,
            params=params,
            timeout=5
        )

        return res.content, res.status_code, res.headers.items()
    except requests.exceptions.ConnectionError:
        return jsonify({"message": f"Service {service_url} is unavailable"}), 503 
    
# Auth Service
@app.route('/registration', methods=['POST'])
def register():
    return forward_request(AUTH_SERVICE_URL, '/registration')

@app.route('/login', methods=['POST'])
def login():
    return forward_request(AUTH_SERVICE_URL, '/login')

@app.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify(msg="Access Token revoked (Logged out)")

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    resp = requests.post(f"{AUTH_SERVICE_URL}/refresh", json={"identity": current_user})
    return resp.json(), resp.status_code

# Book Service
@app.route('/books', methods=['GET', 'POST'])
@jwt_required() 
def books_list():
    if request.method == 'POST':
        @admin_required()
        def handle_post():
            return forward_request(BOOK_SERVICE_URL, '/books')
        return handle_post()
    else:
        return forward_request(BOOK_SERVICE_URL, '/books')

@app.route('/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def book_detail(book_id):
    endpoint = f"/book/{book_id}"
    if request.method == 'GET':
        return forward_request(BOOK_SERVICE_URL, endpoint)
    else:
        @admin_required()
        def handle_modification():
            return forward_request(BOOK_SERVICE_URL, endpoint)
        return handle_modification()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)