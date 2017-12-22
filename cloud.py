from google.cloud import storage
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'journal-hub-50781-firebase-adminsdk-vc4qi-8ffbbce50a.json'

client = storage.Client()
bucket = client.bucket('journal-hub-50781.appspot.com')
blob = bucket.blob('/')
blob.download_as_string()