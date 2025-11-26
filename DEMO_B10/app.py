# app.py

import logging
import time
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from pythonjsonlogger import jsonlogger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics

# ==========================================
# PHẦN 1: KHỞI TẠO & CẤU HÌNH (SETUP)
# ==========================================

app = Flask(__name__)
api = Api(app)

# 1. Setup Rate Limiter (Chống Spam)
# - storage_uri="memory://": Lưu bộ đếm trong RAM (Dùng Redis cho Prod)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "10 per hour"],
    storage_uri="memory://"
)

# 2. Setup Prometheus Metrics (Đo lường)
metrics = PrometheusMetrics(app)
# Tạo một Metric riêng để đếm số sách được tạo
# Label 'genre' giúp ta biết thể loại nào được tạo nhiều nhất
books_created_counter = metrics.counter(
    'books_created_total', 
    'Total number of books created',
    labels={'genre': lambda: request.json.get('genre', 'unknown')}
)

book_view_counter = metrics.counter(
    'book_view_total',
    'Total number of book detail views',
    labels={'book_id': lambda: request.view_args.get('book_id')}
)

# 3. Setup JSON Logger (Ghi nhật ký)
logger = logging.getLogger()
logHandler = logging.StreamHandler()
# Format log: Thêm thời gian, mức độ lỗi, và message
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# ==========================================
# PHẦN 2: DATABASE GIẢ LẬP (MOCK DB)
# ==========================================
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "genre": "Tech"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andy Hunt", "genre": "Tech"}
]

# ==========================================
# PHẦN 3: LOGIC API (RESOURCES)
# ==========================================

class BookList(Resource):
    # --- RATE LIMIT ---
    # Chặn Bot cào dữ liệu: Chỉ cho phép lấy danh sách 5 lần/phút
    decorators = [limiter.limit("5 per minute")]

    def get(self):
        """Lấy danh sách tất cả sách"""
        # --- LOGGING ---
        # Ghi lại hành động lấy danh sách (hữu ích để audit)
        logger.info("Fetching book list", extra={
            "ip": request.remote_addr,
            "total_books": len(BOOKS)
        })
        book_view_counter.inc()
        return {"data": BOOKS, "count": len(BOOKS)}, 200

    def post(self):
        """Thêm sách mới"""
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, help="Title cannot be blank")
        parser.add_argument('author', required=True)
        parser.add_argument('genre', default="General")
        args = parser.parse_args()

        new_book = {
            "id": len(BOOKS) + 1,
            "title": args['title'],
            "author": args['author'],
            "genre": args['genre']
        }
        BOOKS.append(new_book)

        # --- METRICS ---
        # Tăng biến đếm sách lên 1. Prometheus sẽ tự gắn label genre vào.
        books_created_counter.inc()

        # --- LOGGING ---
        # Log chi tiết sách vừa tạo để truy vết nếu có lỗi dữ liệu sau này
        logger.info("New book added", extra={
            "book_id": new_book['id'],
            "title": new_book['title'],
            "author": new_book['author']
        })

        return {"message": "Book created", "book": new_book}, 201

class BookDetail(Resource):
    def get(self, book_id):
        """Xem chi tiết một cuốn sách"""
        book = next((b for b in BOOKS if b['id'] == book_id), None)
        
        if book:
            return {"data": book}, 200
        
        # --- LOGGING ERROR ---
        # Nếu khách tìm sách không có -> Log warning để biết khách đang tìm cái gì
        logger.warning("Book not found", extra={"book_id": book_id})
        return {"message": "Book not found"}, 404

    def delete(self, book_id):
        """Xóa sách"""
        global BOOKS
        # Lọc bỏ sách có id tương ứng
        BOOKS = [b for b in BOOKS if b['id'] != book_id]
        
        logger.info("Book deleted", extra={"book_id": book_id, "performed_by": "admin"})
        return {"message": "Book deleted"}, 200

# Đăng ký URL
api.add_resource(BookList, '/books')
api.add_resource(BookDetail, '/books/<int:book_id>')

if __name__ == '__main__':
    app.run(debug=True)