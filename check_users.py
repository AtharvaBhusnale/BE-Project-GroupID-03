import firebase_admin
from firebase_admin import credentials, firestore, auth

def check_users():
    print("Initializing Firebase...")
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    print("\n--- Firebase Auth Users ---")
    page = auth.list_users()
    auth_users = []
    while page:
        for user in page.users:
            auth_users.append({'uid': user.uid, 'email': user.email})
        page = page.get_next_page()
    
    print(f"Found {len(auth_users)} users in Auth:")
    for u in auth_users:
        print(f" - {u['uid']}: {u['email']}")

    print("\n--- Firestore Collections ---")
    collections = db.collections()
    for coll in collections:
        print(f"Collection: {coll.id}")
        docs = coll.limit(5).stream()
        for doc in docs:
            print(f"  - Doc: {doc.id} => {doc.to_dict()}")

if __name__ == '__main__':
    check_users()
