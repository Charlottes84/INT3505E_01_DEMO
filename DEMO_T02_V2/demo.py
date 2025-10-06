from flask import Flask, request, url_for
from flask_restful import Resource, Api
import uuid
from datetime import datetime # Giữ lại nếu bạn muốn dùng sau này

app = Flask(__name__)
api = Api(app)
app.config['RESTFUL_JSON'] = {'indent': 2, 'sort_keys': False} # Để JSON dễ đọc hơn

# Danh sách sách (sử dụng dictionary để dễ dàng truy cập theo ID)
# Khởi tạo dữ liệu sách
books_data = {
    '0001': {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "isbn": "9780547928227", "is_borrowed": False},
    '0002': {"title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "9780141439518", "is_borrowed": False},
    '0003': {"title": "1984", "author": "George Orwell", "isbn": "9780451524935", "is_borrowed": False}
}

# --- Helper function để thêm các liên kết HATEOAS ---
# Sử dụng _external=True để tạo ra URL đầy đủ
def add_book_links(book_id, book_info):
    links = {
        "self": {"href": url_for('bookresource', book_id=book_id, _external=True), "method": "GET"},
        "update": {"href": url_for('bookresource', book_id=book_id, _external=True), "method": "PUT"},
        "delete": {"href": url_for('bookresource', book_id=book_id, _external=True), "method": "DELETE"}, # Giả định có thể xóa
    }
    
    if book_info["is_borrowed"]:
        links["return"] = {"href": url_for('bookreturnaction', book_id=book_id, _external=True), "method": "POST"}
    else:
        links["borrow"] = {"href": url_for('bookborrowaction', book_id=book_id, _external=True), "method": "POST"}
    
    return links

# --- API Endpoints ---

class BookList(Resource): 
    def get(self): 
        """Lấy danh sách tất cả các cuốn sách với các liên kết HATEOAS."""
        response_books = {}
        for book_id, book_info in books_data.items():
            book_with_links = book_info.copy() # Tạo bản sao để không sửa đổi dữ liệu gốc
            book_with_links["_links"] = add_book_links(book_id, book_info)
            response_books[book_id] = book_with_links
            
        return response_books, 200
    
    def post(self):
        """Thêm một cuốn sách."""
        data = request.get_json()
        if not data or not all(
            key in data for key in ['title', 'author', 'isbn']
        ):
            return {'message': 'Missing data for book creation (title, author, isbn required)'}, 400
        
        # Kiểm tra ISBN duy nhất
        if any(book['isbn'] == data['isbn'] for book in books_data.values()):
            return {'message': 'Book with this ISBN already exists'}, 409
        
        new_book_id = str(uuid.uuid4())
        new_book = {
            "id": new_book_id,
            "title": data['title'],
            "author": data['author'],
            "isbn": data['isbn'],
            "is_borrowed": False # Mặc định sách mới là chưa mượn
        }
        books_data[new_book_id] = new_book
        
        # Thêm liên kết HATEOAS cho sách mới được tạo
        response_data = new_book.copy()
        response_data["_links"] = add_book_links(new_book_id, new_book)
        
        return response_data, 201 

class BookResource(Resource): 
    def get(self, book_id):
        """Lấy thông tin chi tiết của một cuốn sách theo ID, bao gồm các liên kết hành động."""
        book = books_data.get(book_id)
        if not book:
            return {'message': f'Book with ID {book_id} not found'}, 404
        
        response_data = book.copy()
        response_data["_links"] = add_book_links(book_id, book)
        return response_data, 200
    
    def put(self, book_id):
        """Cập nhật thông tin một cuốn sách."""
        book = books_data.get(book_id)
        if not book:
            return {'message': f'Book with ID {book_id} not found'}, 404
        
        data = request.get_json()
        if not data:
            return {'message': 'No data provided for update'}, 400
        
        # Cập nhật các trường
        book['title'] = data.get('title', book['title'])
        book['author'] = data.get('author', book['author'])
        
        if 'isbn' in data and data['isbn'] != book['isbn']:
            # Kiểm tra ISBN duy nhất khi cập nhật
            if any(b['isbn'] == data['isbn'] for bid, b in books_data.items() if bid != book_id):
                return {'message': 'Another book with this ISBN already exists'}, 409
            book['isbn'] = data['isbn']
        
        # is_borrowed không nên được cập nhật trực tiếp qua PUT, mà qua các hành động mượn/trả
        
        response_data = book.copy()
        response_data["_links"] = add_book_links(book_id, book) # Cập nhật lại links sau khi sửa đổi
        return response_data, 200

    def delete(self, book_id):
        """Xóa một cuốn sách."""
        if book_id in books_data:
            del books_data[book_id]
            return {'message': f'Book with ID {book_id} deleted successfully'}, 200
        return {'message': f'Book with ID {book_id} not found'}, 404


class BookBorrowAction(Resource): 
    def post(self, book_id):
        """Mượn một cuốn sách."""
        book = books_data.get(book_id)

        if not book: 
            return {"message": f"Book with ID {book_id} not found"}, 404 
        if book["is_borrowed"]:
            # Trả về 400 và vẫn cung cấp các liên kết (đã mượn thì có thể trả)
            return {"message": "Book is already borrowed", 
                    "_links": add_book_links(book_id, book)}, 400
        
        book["is_borrowed"] = True
        response_data = {"message": f"Book '{book['title']}' borrowed successfully", "book_id": book_id}
        response_data["_links"] = add_book_links(book_id, book) # Cập nhật links sau khi mượn
        return response_data, 200

class BookReturnAction(Resource): 
    def post(self, book_id):
        """Trả một cuốn sách."""
        book = books_data.get(book_id)
        if not book:
            return {"message": f"Book with ID {book_id} not found"}, 404 
        if not book["is_borrowed"]:
            # Trả về 400 và vẫn cung cấp các liên kết (chưa mượn thì có thể mượn)
            return {"message": "Book is not currently borrowed", 
                    "_links": add_book_links(book_id, book)}, 400 
        
        book["is_borrowed"] = False 
        response_data = {"message": f"Book '{book['title']}' returned successfully", "book_id": book_id}
        response_data["_links"] = add_book_links(book_id, book) # Cập nhật links sau khi trả
        return response_data, 200
    
# Đăng ký các Resource với API
api.add_resource(BookList, '/books')
api.add_resource(BookResource, '/books/<string:book_id>')
api.add_resource(BookBorrowAction, '/books/<string:book_id>/borrow') # Endpoint riêng cho mượn
api.add_resource(BookReturnAction, '/books/<string:book_id>/return') # Endpoint riêng cho trả

if __name__ == '__main__': 
    app.run(debug=True)