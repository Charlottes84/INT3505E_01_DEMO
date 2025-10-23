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
    version='1.0',
    title='Demo API + JWT + SQLite',
    description='API uses Flask, JWT and store user data in SQLite',
    authorizations=infojwt 
)


# auth ~ blueprint
auth_ns = api.namespace('auth', description='Xác thực (đăng nhập/đăng ký)')
protected_ns = api.namespace('protected', description='Tài nguyên được bảo vệ')

auth_parser =reqparse.RequestParser()
auth_parser.add_argument('username', type=str, required=True, help='Tên đăng nhập')
auth_parser.add_argument('password', type=str, required=True, help='Mật khẩu')

@auth_ns.route('/registration')
class Registration(Resource):
    @auth_ns.doc('registration_user')
    @auth_ns.expect(auth_parser)
    def post(self):
        args = auth_parser.parse_args()
        username = args['username']
        password = args['password']

        if User.query.filter_by(username=username).first():
            return {
                'message': 'Tên đăng nhập đã tồn tại'
            }, 400
        
        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return {
            'message': f'Người dùng {username} đã được tạo thành công'
        }, 201
    
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('login_user')
    @auth_ns.expect(auth_parser)
    def post(self):
        args = auth_parser.parse_args()
        username = args['username']
        password = args['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
        
        return {
            'message': 'Sai tên đăng nhập hoặc mật khẩu'
        }, 401
    
@protected_ns.route('/data')
class ProtectedData(Resource):

    @jwt_required()
    @api.doc(security='jwt')

    def get(self):
        current_user = get_jwt_identity()
        return {
            'message': f'{current_user} đã truy cập thành công vào tài nguyên!'
        }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


