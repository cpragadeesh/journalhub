from doaj.retriever import OJ
from arxiv.arxiv_extractor import extract_from_arxiv
from pymongo import MongoClient

conn = MongoClient('mongodb://venkat:mongo@DESKTOP-B9O8E12:27017/hub')

db = conn.hub   #MongoDB Connection

topics = db.topics
topiclist = topics.find()

D = OJ()    #DOAJ

def fetch(topic):
    doaj = 'http://doaj.org/api/v1/'
    query = 'search/articles/'+topic+'?page=1&pageSize=100&sort=year%3Adesc'
    api = doaj + query
    D.retriever(api)

for topic in topiclist:
    print(topic['topic'])
    fetch(topic['topic'].replace(' ', '%20'))

    papers = db[topic['topic']]
    for title in D.titles:
        try:
            insertJSON = {'title': title,
                        'abstract': D.abstract[title],
                        'keywords': D.keywords[title],
                        'link': D.link[title],
                        'year': D.year[title]
                    }
            papers.insert_one(insertJSON)            
        except:
            continue