from flask import Flask
from flask_restful import Api
from versions.book_v1 import BookListV1
from versions.book_v2 import BookListV2

app = Flask(__name__)
api = Api(app)

api.add_resource(BookListV1, "/api/v1/books")
api.add_resource(BookListV2, "/api/v2/books")

if __name__ == "__main__":
    app.run(debug=True)