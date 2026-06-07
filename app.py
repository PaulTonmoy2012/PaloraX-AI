from flask import Flask, request, jsonify
#from pymongo import MongoClient
from flask_cors import CORS
#import os

import dotenv

from config import SECRET_KEY
from routes.auth_routes import register_auth_routes
from routes.conversation_routes import register_conversation_routes
from routes.chat_routes import register_chat_routes
from routes.memory_routes import register_memory_routes
from routes.analytics_routes import register_analytics_routes 


dotenv.load_dotenv()


#flask install
  
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)
app.secret_key = SECRET_KEY

#resgister_chat_route
register_chat_routes(app)
register_auth_routes(app)
register_conversation_routes(app)
register_memory_routes(app)
register_analytics_routes(app)

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
    app.run(debug=True, port=5002)
