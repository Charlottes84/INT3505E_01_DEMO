#Server(Flask)
from flask import Flask, request, url_for
from flask_restful import Resource, Api
from datetime import datetime 
import uuid 

app = Flask(__name__)
api = Api(app)

# Danh sách sách
books_data = [
    {"id": str(uuid.uuid4()), "title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "isbn": "9780547928227", "is_borrowed": False},
    {"id": str(uuid.uuid4()), "title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "9780141439518", "is_borrowed": False},
    {"id": str(uuid.uuid4()), "title": "1984", "author": "George Orwell", "isbn": "9780451524935", "is_borrowed": False}
]

def find_book_by_id(book_id):
    for book in books_data:
        if book['id'] == book_id:
            return book
    return None 

# --- Create HATEOS links ---
def add_book_links(book_dict):
    links = []

    links.append({
        "ref": "self",
        "href": url_for('bookresource', book_id=book_dict['id'], _external=True),
        "method": "GET"
    })

    links.append({
        "ref": "update",
        "href": url_for('bookresource', book_id=book_dict['id'], _external=True),
        "method": "PUT"
    })

    if book_dict['is_borrowed']:
        links.append({
            "ref": "return",
            "href": url_for('bookreturn', book_id=book_dict['id'], _external=True),
            "method": "POST"
        })
    else : 
        links.append({
            "ref": "return",
            "href": url_for('bookreturn', book_id=book_dict['id'], _external=True),
            "method": "POST"
        })

    return links
    

#--- API Endpoints ---
class BookList(Resource): 
    def get(self): 
        """Lấy danh sách tất cả các cuốn sách"""
        """Update : HATEOS"""
        book_with_links=[]
        for book in books_data:
            book_copy = book.copy()
            book_copy['links'] = add_book_links(book_copy)
            book_with_links.append(book_copy)
        
        collection_links = [
            {
                "ref": "self",
                "href": url_for('booklist', _external=True),
                "method": "GET"
            },
            {
                "ref": "add_book",
                "href": url_for('booklist', _external=True),
                "method": "POST"
            }
        ]

        return {"_links": collection_links, "books": book_with_links}, 200 
    
    def post(self):
        """Thêm một cuốn sách"""
        data = request.get_json()
        if not data or not all(
            key in data for key in ['title', 'author', 'isbn']
        ):
            return {'message': 'Missing data for book creation'}, 400
        
        if any(book['isbn'] == data['isbn'] for book in books_data):
            return {'message': 'Book with this ISBN already exists'}, 409
        
        new_book = {
            "id": str(uuid.uuid4()),
            "title": data['title'],
            "author": data['author'],
            "isbn": data['isbn'],
            "is_borrowed": False
        }
        books_data.append(new_book)

        response_book = new_book.copy()
        response_book['links'] = add_book_links(response_book)

        return response_book, 201

class BookResource(Resource): 
    def get(self, book_id):
        book = find_book_by_id(book_id)
        if not book:
            return {'message': 'Book not found'}, 404
        
        response_book = book.copy()
        response_book['links'] = add_book_links(response_book)
        return response_book, 200

    
    def post(self, book_id):
        """Mượn một cuốn sách"""
        book = find_book_by_id(book_id)

        if not book: 
            return {"message": "Book not found"}, 404 
        if book["is_borrowed"]:
            return {"message": "Book is already borrowed"}, 400
        
        book["is_borrowed"] = True

        response_book = book.copy()
        response_book['links'] = add_book_links(response_book)
        return {"message": f"Book '{book['title']}' borrowed successfully", "book": response_book}, 200
    
    def put(self, book_id):
        book = find_book_by_id(book_id)
        if not book:
            return {'message': 'Book not found'}, 404
        
        data = request.get_json()
        if data:
            book['title'] = data.get('title', book['title'])
            book['author'] = data.get('author', book['author'])
            if 'isbn' in data and data['isbn'] != book['isbn']:
                if any(b['isbn'] == data['isbn'] for b in books_data if b['id'] != book_id):
                    return {'message': 'Another book with this ISBN already exists'}, 409
                book['isbn'] = data['isbn']
            response_book = book.copy()
            response_book['links'] = add_book_links(response_book)
            return response_book, 200
        return {'message': 'No data provided for update'}, 400


class BookReturn(Resource): 
    def post(self, book_id):
        """Trả một cuốn sách"""
        book = books_data.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404 
        if not book["is_borrowed"]:
            return {"message": "Book is not currently borrowed"}, 400 
        
        book["is_borrowed"] = False 
        response_book = book.copy()
        response_book['links'] = add_book_links(response_book)
        return {"message": f"Book '{book['title']}' returned successfully", "book": response_book}, 200
    
api.add_resource(BookList, '/books', endpoint='booklist')
api.add_resource(BookResource, '/books/<string:book_id>', endpoint='bookresource')
api.add_resource(BookReturn, '/books/<string:book_id>/return', endpoint='bookreturn')

if __name__ == '__main__': 
    app.run(debug=True)
    


