import firebase_admin
from firebase_admin import credentials, firestore, auth

def delete_all_users():
    print("Initializing Firebase...")
    try:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass # App already initialized
        
    db = firestore.client()
    
    # 1. Delete from Firebase Auth
    print("\n--- Deleting Firebase Auth Users ---")
    page = auth.list_users()
    deleted_auth_count = 0
    while page:
        for user in page.users:
            print(f"Deleting Auth user: {user.uid} ({user.email})")
            auth.delete_user(user.uid)
            deleted_auth_count += 1
        page = page.get_next_page()
    print(f"Total Auth users deleted: {deleted_auth_count}")

    # 2. Delete from Firestore 'users' collection
    print("\n--- Deleting Firestore 'users' Collection Data ---")
    users_ref = db.collection('users')
    docs = users_ref.stream()
    deleted_db_count = 0
    for doc in docs:
        print(f"Deleting Firestore document: {doc.id}")
        doc.reference.delete()
        deleted_db_count += 1
    print(f"Total Firestore user documents deleted: {deleted_db_count}")
    
    # Check if there's a 'patients' collection and ask to manually check if not specified in plan
    print("\nNote: Only the 'users' collection was cleared. Other collections (like 'patients', 'audit_logs') were left intact as per plan.")

if __name__ == '__main__':
    delete_all_users()
