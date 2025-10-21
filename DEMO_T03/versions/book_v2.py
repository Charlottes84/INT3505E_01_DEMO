from flask_restful import Resource, reqparse
from data import books

class BookListV2(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("author", type=str, required=False, location="args", help="lọc theo tên tác giả")
        args = parser.parse_args()

        filtered_books = []
        if args["author"]:
            for b in books:
                if args["author"].lower() in b["author"].lower():
                    filtered_books.append(b)
        else:
            filtered_books = books

        response = {
            "metadata": {
                "total": len(filtered_books),
                "version": "v2",
            },
            "books": filtered_books
        }

        return response, 200
