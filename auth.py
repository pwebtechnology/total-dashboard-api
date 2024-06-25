import jwt
from collections import defaultdict
from variables import *
from functions import *
from api import *
from main import *

app.config['secret_key'] = "CD42F6C8314FDD9A8427CCE1495AE44F1C8B456E1039257A87BD0BA6275E4918" #generated from website - just for testing will change after tests passed

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'token is missing'}), 403
        try:
            jwt.decode(token, app.config['secret_key'], algorithms="HS256")
        except Exception as error:
            return jsonify({'error': 'token is invalid or expired'})
        return f(*args, **kwargs)
    return decorated
