import firebase_admin
from firebase_admin import credentials, firestore, auth

try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
except ValueError:
    pass

db = firestore.client()

def create_test_doctor():
    doctor_uid = "doc_1"
    email = "atharvaabhusnale@gmail.com"
    password = "Atharva@10"
    
    try:
        auth.create_user(uid=doctor_uid, email=email, password=password)
        print("Created auth user")
    except:
        print("Auth user already exists")

    db.collection('users').document(doctor_uid).set({
        'name': 'Dr. Shaun Murphy',
        'role': 'doctor',
        'doctorCode': 'DOC123',
        'email': email
    })
    print("Doctor user created/updated in Firestore with code DOC123")

if __name__ == "__main__":
    create_test_doctor()
