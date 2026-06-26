import firebase_admin, json
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

users_dict = {}
for doc in db.collection('users').stream():
    users_dict[doc.id] = doc.to_dict()

with open('users_out.json', 'w') as f:
    json.dump(users_dict, f, indent=2)
