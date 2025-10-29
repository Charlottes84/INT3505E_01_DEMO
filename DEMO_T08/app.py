from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, marshal_with, fields
from sqlalchemy.orm import joinedload, selectinload 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
api = Api(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    books = db.relationship('Book', backref='author', lazy='select')

    def __repr__(self):
        return f'<Author {self.name}>'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

def init_db():
    with app.app_context():
        db.create_all()

        db.session.query(Book).delete()
        db.session.query(Author).delete()
        db.session.commit()

        author1 = Author(name='J.K.Rowling')
        author2 = Author(name='Nam Cao')
        db.session.add_all([author1, author2])
        db.session.commit()

        db.session.add_all([
            Book(title='Harry Potter 1', author_id=author1.id),
            Book(title='Harry Potter 2', author_id=author1.id),
            Book(title='Lao Hac 1', author_id=author2.id),
            Book(title='Lao Hac 2', author_id=author2.id),
            Book(title='Lao Hac 3', author_id=author2.id)
        ])
        db.session.commit()

        print("Database initialized with 5 books and 2 authors.")

author_fields = {
    'name': fields.String,
}

book_fields = {
    'title': fields.String, 
    'author': fields.Nested(author_fields), 
}

# N + 1 queries 
class BookList_NPlusOne(Resource):
    @marshal_with(book_fields)
    def get(self):
        books = Book.query.all()

        return books 

api.add_resource(BookList_NPlusOne, '/books/n+1')


# Joined Loading
class BookList_Joined(Resource):
    @marshal_with(book_fields)
    def get(self):
        books = db.session.excute(
            db.select(Book).options(joinedload(Book.author))
        ).scalars().all()

        return books
    
api.add_resource(BookList_Joined, '/books/joined') 

# Batch loading 
class BookList_SelectIn(Resource):
    @marshal_with(book_fields)
    def get(self):
        books = db.session.excute(
            db.select(Book).options(selectinload(Book.author))
        ).scalars.all()

api.add_resource(BookList_SelectIn, '/books/selectin')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)