from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    jwt_refresh_token_required,
    JWTManager,
    get_jwt,
    unset_jwt_cookies
)
from datetime import timedelta
import redis

app = Flask(__name__)
api = Api(app)

app.config["JWT_SECRET_KEY"] = "advanced-secret-key-for-refresh-token"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=15)  
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)    

jwt = JWTManager(app)
blocklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blocklist

USERS = {
    "secure_user": {"password": "abc", "roles": ["user"]},
}

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
            refresh_token = create_refresh_token(identity=username)
            
            return jsonify(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in_seconds=app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds(),
                msg="Login successful. Access Token is short-lived for security."
            )
        
        return {"msg": "Bad username or password"}, 401

class TokenRefresh(Resource):
    @jwt_refresh_token_required()
    def post(self):
        current_user = get_jwt_identity()
        
        new_access_token = create_access_token(identity=current_user)
        
        return jsonify(
            access_token=new_access_token,
            msg="Access Token has been refreshed."
        )

class Logout(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        
        blocklist.add(jti)
        
        response = jsonify({"msg": "Successfully logged out. Access Token has been revoked."})
        unset_jwt_cookies(response) 
        
        return response

class Protected(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        jti = get_jwt()["jti"]
        
        return jsonify(
            hello=f"Hello, {current_user}!",
            token_id=jti,
            msg="This data is protected by a short-lived Access Token."
        )

api.add_resource(Login, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(Logout, "/logout")
api.add_resource(Protected, "/protected")

if __name__ == "__main__":
    app.run(debug=True)