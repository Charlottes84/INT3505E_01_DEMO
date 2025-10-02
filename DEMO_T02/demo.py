from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime
import uuid # Dùng để tạo ID duy nhất cho các đối tượng

app = Flask(__name__)
api = Api(app)

# --- Dữ liệu "in-memory" thay thế database ---
# Chúng ta sẽ dùng dictionaries để mô phỏng các bảng
# ID sẽ được tạo tự động bằng uuid hoặc đơn giản là một counter

# Danh sách sách
books_data = [
    {"id": str(uuid.uuid4()), "title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "isbn": "9780547928227", "available": True},
    {"id": str(uuid.uuid4()), "title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "9780141439518", "available": True},
    {"id": str(uuid.uuid4()), "title": "1984", "author": "George Orwell", "isbn": "9780451524935", "available": True}
]

# Danh sách các lượt mượn
loans_data = []

# --- Helper functions để tìm kiếm dữ liệu ---
def find_book_by_id(book_id):
    for book in books_data:
        if book['id'] == book_id:
            return book
    return None

def find_loan_by_id(loan_id):
    for loan in loans_data:
        if loan['id'] == loan_id:
            return loan
    return None

# --- API Resources ---

class BookList(Resource):
    def get(self):
        return books_data, 200

    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ['title', 'author', 'isbn']):
            return {'message': 'Missing data for book creation'}, 400
        
        # Kiểm tra ISBN trùng lặp
        if any(book['isbn'] == data['isbn'] for book in books_data):
            return {'message': 'Book with this ISBN already exists'}, 409

        new_book = {
            "id": str(uuid.uuid4()), # Tạo ID duy nhất
            "title": data['title'],
            "author": data['author'],
            "isbn": data['isbn'],
            "available": True
        }
        books_data.append(new_book)
        return new_book, 201

class BookResource(Resource):
    def get(self, book_id):
        book = find_book_by_id(book_id)
        if not book:
            return {'message': 'Book not found'}, 404
        return book, 200

    def put(self, book_id):
        book = find_book_by_id(book_id)
        if not book:
            return {'message': 'Book not found'}, 404
        
        data = request.get_json()
        if data:
            book['title'] = data.get('title', book['title'])
            book['author'] = data.get('author', book['author'])
            # Cẩn thận khi cập nhật ISBN, có thể cần kiểm tra trùng lặp
            if 'isbn' in data and data['isbn'] != book['isbn']:
                if any(b['isbn'] == data['isbn'] for b in books_data if b['id'] != book_id):
                    return {'message': 'Another book with this ISBN already exists'}, 409
                book['isbn'] = data['isbn']
            return book, 200
        return {'message': 'No data provided for update'}, 400

    def delete(self, book_id):
        global books_data # Cần global để sửa đổi list bên ngoài hàm
        book = find_book_by_id(book_id)
        if not book:
            return {'message': 'Book not found'}, 404
        
        # Đảm bảo sách không đang được mượn
        if any(loan['book_id'] == book_id and loan['return_date'] is None for loan in loans_data):
            return {'message': 'Cannot delete book as it is currently on loan'}, 409

        books_data = [b for b in books_data if b['id'] != book_id]
        return {'message': 'Book deleted successfully'}, 204 # No Content

class LoanList(Resource):
    def get(self):
        return loans_data, 200

class LoanBook(Resource): # Đổi tên để tránh xung đột với LoanResource bên dưới
    def post(self, book_id):
        book = find_book_by_id(book_id)
        if not book:
            return {'message': 'Book not found'}, 404

        if not book['available']:
            return {'message': 'Book is currently not available for loan'}, 409
        
        new_loan = {
            "id": str(uuid.uuid4()),
            "book_id": book['id'],
            "loan_date": datetime.utcnow().isoformat(),
            "return_date": None # Null if not returned yet
        }
        loans_data.append(new_loan)
        book['available'] = False # Mark book as unavailable
        
        return {'message': f'Book "{book["title"]}" loaned successfully', 'loan': new_loan}, 201

class ReturnBook(Resource): # Đổi tên để rõ ràng hơn
    def put(self, loan_id):
        loan = find_loan_by_id(loan_id)
        if not loan:
            return {'message': 'Loan not found'}, 404
        
        if loan['return_date']:
            return {'message': 'Book has already been returned'}, 409
        
        loan['return_date'] = datetime.utcnow().isoformat()
        
        book = find_book_by_id(loan['book_id'])
        if book:
            book['available'] = True # Mark book as available again
        
        return {'message': f'Book returned successfully', 'loan': loan}, 200

# --- API Endpoints ---
api.add_resource(BookList, '/books')
api.add_resource(BookResource, '/books/<string:book_id>') # book_id giờ là string (UUID)
api.add_resource(LoanList, '/loans')
api.add_resource(LoanBook, '/books/<string:book_id>/loan') # book_id giờ là string (UUID)
api.add_resource(ReturnBook, '/loans/<string:loan_id>/return') # loan_id giờ là string (UUID)


if __name__ == '__main__':
    app.run(debug=True)