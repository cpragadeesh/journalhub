import pyrebase
import os

config = {
  "apiKey": "AIzaSyBeayOZq_HHpLmv0jipAEyHC_YIE5udSkY",
  "authDomain": "journal-hub-50781.firebaseapp.com",
  "databaseURL": "https://journal-hub-50781.firebaseio.com",
  "storageBucket": "journal-hub-50781.appspot.com",
  "serviceAccount": "journal-hub-50781-firebase-adminsdk-vc4qi-8ffbbce50a.json"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
users = db.child("/users").get()

people = []

for uid in users.val():
    email = users.val()[uid]['email']
    keys = users.val()[uid]['keys']
    user = {'uid':uid, 'email':email, 'keys':keys}
    people.append(user)


storage = firebase.storage()

#print(storage.child('EgtsZpR6L0Rm53dXVsBDI5shn843/pele1.jpeg').get_url(''))

for user in people:
    print(user['uid'])
    if not os.path.exists('firebase-storage/'+user['uid']):
        os.makedirs('firebase-storage/'+user['uid'])

    #storage.child('EgtsZpR6L0Rm53dXVsBDI5shn843/pele1.jpeg').download('pele1.jpeg')
    #storage.child('/'+user['uid']+'/').download('firebase-storage/'+user['uid']+'/')
    

# Remember: Go to https://console.cloud.google.com/iam-admin/iam/project?project=journal-hub-50781
# Give "Storage Admin" role to firebase sdk for firebase storage bucket access 

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate('journal-hub-50781-firebase-adminsdk-vc4qi-8ffbbce50a.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'journal-hub-50781.appspot.com'
})

bucket = storage.bucket('journal-hub-50781.appspot.com/EgtsZpR6L0Rm53dXVsBDI5shn843')
print(bucket)