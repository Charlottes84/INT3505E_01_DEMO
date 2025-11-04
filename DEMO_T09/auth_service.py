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
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1)
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
        return self.roles.split(',')

# API 
class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        roles = data.get("roles")

        if User.query.filter_by(username=username).first():
            return {"message": "Username already exists"}, 400
        
        new_user = User(username=username, roles=roles)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created successfully"}, 201
    
class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get("username")).first()

        if not user or not user.check_password(data.get("password")):
            return {"message": "Bad username or password"}, 401 
        
        access_token = create_access_token(
            identity=user.username,
            additional_claims={"roles": user.get_roles_list()}
        )

        refresh_token = create_refresh_token(identity=user.username)
        return jsonify(access_token=access_token, refresh_token=refresh_token)

class TokenRefresh(Resource):
    def post(self):
        identity = request.json.get('identity')
        user = User.query.filter_by(username=identity).first()

        if not user:
            return {"message": "User not found"}, 404 
        
        new_access_token = create_access_token(
            identity=user.username,
            additional_claims={"roles": user.get_roles_list()}
        )

        return jsonify(access_token=new_access_token)
    
api.add_resource(UserRegister, "/registration")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5001, debug=True)
