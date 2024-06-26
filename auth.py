import jwt
from collections import defaultdict
from variables import *
from functions import *
from api import *
from main import *
from flask_login import LoginManager, UserMixin, login_user, logout_user

#app.config['secret_key'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918" #generated from website - just for testing will change after tests passed


async def password_check():
    database = user_creds_params['database']
    collection = user_creds_params['collection']
    query = user_creds_params['query']
    mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    try:
        db = mongo_client.database
        col = db.collection
        cursor = col.aggregate(query)
        return jsonify(cursor)
    finally :
        mongo_client.close()

