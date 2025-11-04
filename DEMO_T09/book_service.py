# book_service.py

from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import os 

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "book.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

api = Api(app)
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author
        }
    
class BookList(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)

        books = pagination.items

        return jsonify(
            books=[book.to_dict() for book in books],
            total_pages=pagination.pages, 
            current_page=pagination.page,
            total_books=pagination.total
        )
    
    def post(self):
        data = request.get_json()
        new_book = Book(title=data.get("title"), author=data.get("author"))
        db.session.add(new_book)
        db.session.commit()
        return new_book.to_dict(), 201
    
class BookResource(Resource):
    def get(self, book_id):
        book = Book.query.get_or_404(book_id)
        return jsonify(book.to_dict())
    
    def put(self, book_id):
        book = Book.query.get_or_404(book_id)
        data = request.get_json()
        book.title = data.get("title", book.title)
        book.author = data.get("author", book.author)
        db.session.commit()

        return jsonify(book.to_dict())
    
    def delete(self, book_id):
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted"}, 200 

api.add_resource(BookList, "/books")
api.add_resource(BookResource, "/books/<int:book_id>")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5002, debug=True)