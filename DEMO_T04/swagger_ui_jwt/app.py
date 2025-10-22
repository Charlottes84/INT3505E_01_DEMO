import os
from flask import Flask, jsonify
from flask_restx import Api, Resource, reqparse
from flask_jwt_extended import (create_access_token, get_jwt_identity, jwt_required, JWTManager)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-demo-key-shouldn't-live-it-like-that"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
infojwt = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter Bearer <token>'
    }
}

api = Api(
    app,
    version='1.0'
    title='Demo API + JWT + SQLite',
    description='API uses Flask, JWT and store user data in SQLite'
    authorizations=infojwt 
)

auth_ns = api.namespace('auth', description='Xác thực (đăng nhập/đăng ký)')
protected_ns = api.namespace('protected', description='Tài nguyên được bảo vệ')

