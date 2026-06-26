import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

count = 0
docs = db.collection('mri_uploads').where('patientName', '==', 'New Patient').stream()
for doc in docs:
    doc.reference.update({'patientName': 'Demo Patient'})
    count += 1

docs2 = db.collection('users').where('name', '==', 'New Patient').stream()
for doc in docs2:
    doc.reference.update({'name': 'Demo Patient'})
    count += 1

print(f"Updated {count} old 'New Patient' entries to 'Demo Patient'")
