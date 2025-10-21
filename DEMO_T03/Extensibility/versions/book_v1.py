from flask_restful import Resource 
from data import books 


class BookListV1(Resource):
    def get(self):
        return {"books": books}, 200
    
