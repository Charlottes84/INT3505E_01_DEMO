from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests

app = Flask(__name__)
api = Api(app)

books = {
    123: {"title": "Dế Mèn phiêu lưu ký", "quantity": 10},
    124: {"title": "Tắt đèn", "quantity": 5}
}

WEBHOOK_URL = "http://127.0.0.1:5000/webhook/book-update"

# Webhook endpoint 
class BookWebhook(Resource):
    def post(self): 
        data = request.get_json()
        book_id = data.get("id")
        title = data.get("title")
        quantity_left = data.get("quantity_left")

        books[book_id] = {"title": title, "quantity": quantity_left}
        print(f'Webhook received: {data}')
        return {"status:" "success"},200
    
# List book
class BookList(Resource):
    def get(self):
        return books, 200
    
# Borrow book
class BorrowBook(Resource):
    def post(self, book_id):
        if book_id in books and books[book_id]["quantity"] > 0:
            books[book_id]["quantity"] -=1
        
            # Send Webhook
            payload = {
                "book_id": book_id,
                "title": books[book_id]["title"],
                "quantity_left": books[book_id]["quantity"],
                "action": "borrowed"
            }
            requests.post(WEBHOOK_URL, json=payload)

            return books, 200
        return {"message": "Book not available"}, 400

class ReturnBook(Resource):
    def post(self, book_id):
        if book_id in books:
            books[book_id]["quantity"] += 1

            payload = {
                "book_id": book_id,
                "title": books[book_id]["title"],
                "quantity_left": books[book_id]["quantity"],
                "action": "returned"
            }
            requests.post(WEBHOOK_URL, json=payload)

            return books, 200
        return {"message": "Book not found"}, 400

api.add_resource(BookWebhook, "/webhook/book-update")
api.add_resource(BookList, "/books")
api.add_resource(BorrowBook, "/borrow/<int:book_id>")
api.add_resource(ReturnBook, "/return/<int:book_id>")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
