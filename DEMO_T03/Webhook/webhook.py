from flask import Flask, request
from flask_restful import Resource, Api
import datetime

app = Flask(__name__)
api = Api(app)

event_log = [] # demo = thay cho database

# App A = Postman
# App B = My laptop 
# webhook.py = xu ly webhook
# terminal = thong bao se nhan duoc 

class BookEventWebhook(Resource):
    def post(self):
        data = request.get_json()

        if not data or 'event_type' not in data or 'payload' not in data:
            return {'message': 'Bad Request: Missing event_type or payload'}, 400
        
        event_type = data.get('event_type')
        payload = data.get('payload')

        log_entry = {
            "received_at": datetime.datetime.now().isoformat(),
            "event": event_type,
            "data": payload
        }
        event_log.append(log_entry)

        # Check webhook received --> in terminal 
        print("--- WEBHOOK RECEIVED ---")
        print(f"Event: {event_type}")
        print(f"User ID: {payload.get('user_id')}")
        print(f"Book ID: {payload.get('book_id')}")
        print("--------------------------------")

        # logic 
        if event_type == 'book_borrowed': 
            # them logic : cap nhat CSDL 
            # thong bao la da muon duoc sach
            print(f"Processing BORROW event for book {payload.get('book_id')}")
        elif event_type == 'book_returned':
            print(f"Processing RETURN event for book {payload.get('book_id')}")
        elif event_type == 'book_lost':
            print(f"Processing LOST event for book {payload.get('book_id')}")
        else:
            print(f"Warning: Received unknown event_type '{event_type}'")
        return {'status': 'success', 'message': f'Event {event_type} received'}, 200

api.add_resource(BookEventWebhook, '/webhook')

if __name__ == '__main__':
    app.run(debug=True)