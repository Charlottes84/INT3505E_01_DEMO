# auth_service.py

from flask import Flask, jsonify, request 
from flask_restful import Resource, Api 
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta 
import os 

 
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "auth.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
app.config["JWT_SECRET_KEY"] = "mot-secret-key-khong-duoc-ghi-o-day"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(mintes=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models (Database)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)

    roles = db.Column(db.String(120), nullable=False, default="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)
    
    def get_roles_list(self):
        return self.roles.split(' - ')

# API 
class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by