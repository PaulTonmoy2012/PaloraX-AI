from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import dotenv

dotenv.load_dotenv()
#flask install
app = Flask(__name__)

#connecting to mongodb

client = MongoClient(os.getenv("MONGO_URI"))

#accessing the database as db
db = client[os.getenv("DATABASE_NAME")]
# routes
@app.route('/add_message', methods=['POST'])
def add_message():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    message = data['message']
    
    result=db.messages.insert_one({'message': message})
    
    return jsonify({'message': 'Message added successfully',
                    "_id": str(result.inserted_id)}), 201


if __name__ == '__main__':
    app.run(debug=True)