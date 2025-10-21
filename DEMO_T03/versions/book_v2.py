from flask_restful import Resource, reqparse
from data import books

class BookListV2(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("author", type=str, required=False, location="args", help="tìm kiếm theo tên tác giả")
        parser.add_argument("sort", type=str, required=False, choices=("author", "year"), location="args")
        args = parser.parse_args()

        filtered_books = []
        if args["author"]:
            for b in books:
                if args["author"].lower() in b["author"].lower():
                    filtered_books.append(b)
        else:
            filtered_books = books

        if args["sort"] == "author":
            filtered_books = sorted(filtered_books, key=lambda b: b["author"])
        elif args["sort"] == "year":
            filtered_books = sorted(filtered_books, key=lambda b: b["year"])

        #Data Extensibility ~ Response Extensibility != Functional Extensibility
        response = {
            "metadata": {
                "version": "v2",
                "total": len(filtered_books),
                "filter_by": {"author": args["author"]} if args["author"] else {},
                "sorted_by": args["sort"] if args["sort"] else None
            },
            "books": filtered_books
        }

        return response, 200
