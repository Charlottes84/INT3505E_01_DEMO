import logging
from pythonjsonlogger import jsonlogger
from flask import Flask, request
from flask_restful import Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from flask_talisman import Talisman

# Khởi tạo App
app = Flask(__name__)
api = Api(app)

# --- 1. SECURITY (Talisman) ---
# force_https=False để test local. Production set True.
Talisman(app, force_https=False)

# --- 2. LOGGING (JSON) ---
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@app.before_request
def log_request_info():
    logger.info("Request Inbound", extra={
        "method": request.method,
        "path": request.path,
        "ip": request.remote_addr
    })

# --- 3. RATE LIMITING ---
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# --- 4. METRICS (Prometheus) ---
metrics = PrometheusMetrics(app)

# --- API RESOURCES ---
class Home(Resource):
    def get(self):
        return {"message": "System is healthy"}

class Login(Resource):
    # Limit login: Chống brute-force
    decorators = [limiter.limit("5 per minute")]
    
    def post(self):
        # Giả lập logic login
        logger.info("User Login Attempt", extra={"user": "admin"})
        return {"token": "abc-xyz-123"}

api.add_resource(Home, '/')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    # Chỉ dùng để debug local
    app.run(debug=True)