import datetime
from functools import wraps
from flask import Flask, request, jsonify, make_response, render_template
from flask_restful import Resource, Api
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
api = Api(app)


app.config['SECRET_KEY'] = 'abc'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(minutes=30)

users = {"public_id": "testuser", "password": "password123"}

#decorator 
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None 

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        elif 'token' in request.cookies:
            token = request.cookies.get('token')
        
        if not token:
            return {'message': 'Token is missing!'}, 401 
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users.get(data['public_id'])
            if not current_user:
                return {'message': 'Token is invalid'}, 401
        except Exception as e:
            return {'message': 'Token is invalid', 'error': str(e)}, 401
        
        return f(current_user, *args, **kwargs)
    return decorated

class Register(Resource):
    def post(self):
        data = request.get_json()
        public_id = data.get('public_id')
        password = data.get('password')

        if not public_id or not password:
            return {'message': 'Missing public_id or password'}, 400

        if public_id in users:
            return {'message': 'User already exists'}, 409

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        users[public_id] = {'password': hashed_password, 'admin': False}
        return {'message': 'Registered successfully!'}, 201
    
class Login(Resource):
    def post(self):
        auth = request.get_json()

        if not auth or not auth.get('public_id') or not auth.get('password'):
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
            
        user = users.get(auth['public_id'])

        if not user or not check_password_hash(user['password'], auth['password']):
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        token = jwt.encode({
            'public_id': user['public_id'] if 'public_id' in user else auth['public_id'],
            'exp': datetime.datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
        }, app.config['SECRET_KEY'], algorithm="HS256")

        resp = make_response({'message': 'Logged in successfully!', 'token': token})

        resp.set_cookie('token', token, httponly=True, samesite='Lax', secure=True, expires=datetime.datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA'])

        return resp
    
class Protected(Resource):
    @token_required
    def get(self, current_user):
        return {'message': f'Hello, {current_user["public_id"]}! This is a protected endpoint.'}

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')    

if __name__ == '__main__':
    app.run(debug=True)