import jwt
from datetime import datetime, timedelta, timezone

key = "7E833965C7DEECD92A5F4F5476573DCEEA40070C2E392A66F4D8479E8232CF1C"

def make_token(data):
    print(data)
    payload = {"name": data['name'], "email": data['email'], "password": data['password'] }
    print(payload)
    token = jwt.encode(payload, key, algorithm='HS256')
    print(token)
    return token

def decode_token(token):
    data = jwt.decode(token, key, algorithms=['HS256'])
    return data

def parseToken(authorizationHeader):
    return authorizationHeader.split(' ')[1]