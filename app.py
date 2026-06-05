from flask import Flask, request, jsonify
#from pymongo import MongoClient
from flask_cors import CORS
#import os
import dotenv

from routes.chat_routes import register_chat_routes

dotenv.load_dotenv()
#flask install
  
app = Flask(__name__)
CORS(app)

#resgister_chat_route
register_chat_routes(app)

@app.route('/',methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the PaloraX AI!'}), 200


#connecting to mongodb

#client = MongoClient(os.getenv("MONGO_URI"))

#accessing the database as db
#db = client[os.getenv("DATABASE_NAME")]
# routes
# @app.route('/add_message', methods=['POST'])
# def add_message():
#     data = request.json
#     if not data or 'message' not in data:
#         return jsonify({'error': 'Message is required'}), 400    
    # message = data['message']
    
    # result=db.messages.insert_one({'message': message})
    
    # return jsonify({'message': 'Message added successfully',
    #                 "_id": str(result.inserted_id)}), 201


if __name__ == '__main__':
    app.run(debug=True)