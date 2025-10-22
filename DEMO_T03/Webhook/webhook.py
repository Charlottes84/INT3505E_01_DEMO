from flask import Flask, request
from flask_restful import Resource, Api
import requests
import datetime

app = Flask(__name__)
api = Api(app)

event_log = [] # demo = thay cho database
borrowed_books_db = []

# App A = Postman
# App B = My laptop 
# webhook.py = xu ly webhook
# terminal = thong bao se nhan duoc 

class BorrowBookAPI(Resource):
    
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        book_id = data.get('book_id')

        due_date = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()

        borrow_record = {
            "user_id": user_id,
            "book_id": book_id,
            "due_date": due_date,
            "notified": False
        }

        borrowed_books_db.append(borrow_record)

        print(f"\n--- 1. API /api/borrow ĐÃ LƯU ---")
        print(f"User '{user_id}' đã mượn sách '{book_id}'. Hạn trả: {due_date}")

        return {
            "message": "Mượn sách thành công!",
            "record": borrow_record
        }, 200 
    
class CheckDueDateAPI(Resource):
    def post(self): 
        print(f"\n--- 2. HỆ THỐNG BẮT ĐẦU QUÉT HẠN TRẢ SÁCH ---")
        
        books_to_notify = [
            book for book in borrowed_books_db if not book.get("notified")
        ]

        if not books_to_notify:
            print("Không có sách nào cần thông báo")
            return {"message": "Không có sách nào cần thông báo"}, 200 
        
        for book in books_to_notify:
            print(f"Phát hiện sách '{book['book_id']}' sắp hết hạn. Đang gọi Webhook thông báo...")

            try:
                requests.post(
                    "http://127.0.0.1:5000/webhook/notify",
                    json={
                        "event_type":"due_date_reminder",
                        "payload": {
                            "user_id": book['user_id'],
                            "book_id": book['book_id'],
                            "due_date": book["due_date"],
                            "message": f"Sách {book['book_id']} của bạn sắp hết hạn vào {book['due_date']}!"                        
                        }
                    }, 
                    timeout=1
                )
                book["notified"]=True
            except requests.exceptions.RequestException as e:
                print(f"Lỗi khi gọi Webhook: {e}")
        return {"message": f"Đã quét và gửi {len(books_to_notify)} thông báo."}, 200
    
class NotificationWebhook(Resource):
    def post(self):
        data = request.get_json()
        payload = data.get('payload', {})

        print(f"\n---  3. WEBHOOK NOTIFY ĐÃ NHẬN LỆNH  ---")
        print(f"Event: {data.get('event_type')}")
        print(f"Đang gửi thông báo cho: {payload.get('user_id')}")
        print(f"Nội dung: {payload.get('message')}")
        print("----------------------------------------------------")
        
        return {'status': 'success'}, 200
    
api.add_resource(BorrowBookAPI, '/api/borrow')
api.add_resource(CheckDueDateAPI, '/api/check_due_dates')
api.add_resource(NotificationWebhook, '/webhook/notify')

if __name__ == "__main__":
    app.run(debug=True)