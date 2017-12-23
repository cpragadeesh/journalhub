from doaj.retriever import OJ
from pymongo import MongoClient

conn = MongoClient('localhost:27017')

db = conn.hub   #MongoDB Connection

data = db.data
topiclist = data.find()

def fetch(topic):
    doaj = 'http://doaj.org/api/v1/'
    query = 'search/articles/'+topic+'?page=1&pageSize=100&sort=year%3Adesc'
    api = doaj + query
    D.retriever(api)

for topic in topiclist:
    print('\n'+topic['_id']+'\n')
    for prefs in topic['keys']:
        D = OJ()    #DOAJ

        print(prefs)
        fetch(prefs.replace(' ', '%20'))

        # Storing with title as the collection name
        papers = db[prefs]
        for title in D.titles:
            try:
                insertJSON = {'_id': title,
                            'abstract': D.abstract[title],
                            'keywords': D.keywords[title],
                            'link': D.link[title],
                            'year': D.year[title],
                            'author': D.author[title],
                            'journal': D.journal[title]
                        }
                papers.insert_one(insertJSON)     
            except:
                continue