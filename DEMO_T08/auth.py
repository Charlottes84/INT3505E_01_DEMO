from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity, JWTManager, get_jwt)
from functools import wraps
import time

app = Flask(__name__)
api = Api(app)

app.config["JWT_SECRET_KEY"] = "super-secret-key-b06-shouldn't-here" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 15  
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 3600 
jwt = JWTManager(app)

USERS = {
    "admin_user": {"password": "123", "roles": ["admin", "editor"]},
    "guest_user": {"password": "123", "roles": ["guest"]},
}

BOOKS = [
    {"id": 1, "title": "Bảo Mật API cơ bản", "author": "Gemini"},
    {"id": 2, "title": "Flask Cookbook", "author": "Google"},
]
next_book_id = 3

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            
            if "admin" not in claims.get("roles", []):
                return {"msg": "Authorization Error: Admin access required"}, 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username", None)
        password = data.get("password", None)

        user_info = USERS.get(username)

        if user_info and user_info["password"] == password:
            access_token = create_access_token(
                identity=username,
                additional_claims={"roles": user_info["roles"]}
            )
            return jsonify(
                access_token=access_token,
                msg="Authentication Successful"
            )
        
        return {"msg": "Bad username or password"}, 401

class BookList(Resource):
    
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return jsonify(
            books=BOOKS,
            current_user=current_user,
            msg="Welcome! You have authenticated successfully."
        )

    @jwt_required()
    @admin_required() 
    def post(self):
        global next_book_id
        
        current_user = get_jwt_identity()

        data = request.get_json()
        new_book = {
            "id": next_book_id,
            "title": data.get("title"),
            "author": data.get("author")
        }
        BOOKS.append(new_book)
        next_book_id += 1
        
        return jsonify(
            book=new_book,
            msg=f"Book added successfully by admin: {current_user}"
        ), 201

api.add_resource(Login, "/login")
api.add_resource(BookList, "/books")

if __name__ == "__main__":
    app.run(debug=True)