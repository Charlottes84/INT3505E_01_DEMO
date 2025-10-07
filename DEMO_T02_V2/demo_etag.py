from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import hashlib
import json

app = Flask(__name__)
api = Api(app)

# Dữ liệu giả định
data = {
    "1": {"name": "Item A", "description": "This is item A."},
    "2": {"name": "Item B", "description": "This is item B."}
}

def generate_etag(resource_data):
    return hashlib.md5(json.dumps(resource_data, sort_keys=True).encode('utf-8')).hexdigest()

class Item(Resource):
    def get(self, item_id):
        if item_id not in data:
            return {"message": "Item not found"}, 404

        item = data[item_id]
        current_etag = generate_etag(item)

        if 'If-None-Match' in request.headers:
            if_none_match = request.headers['If-None-Match'].strip('"') 
            if if_none_match == current_etag:
                return '', 304, {'ETag': f'"{current_etag}"'} 

        return item, 200, {'ETag': f'"{current_etag}"'} 

    def put(self, item_id):
        if item_id not in data:
            return {"message": "Item not found"}, 404

        new_data = request.get_json()
        if not new_data:
            return {"message": "No data provided"}, 400

        data[item_id].update(new_data)
        updated_item = data[item_id]
        updated_etag = generate_etag(updated_item)

        return {"message": "Item updated successfully", "item": updated_item}, 200, {'ETag': f'"{updated_etag}"'}

api.add_resource(Item, '/items/<string:item_id>')

if __name__ == '__main__':
    app.run(debug=True)