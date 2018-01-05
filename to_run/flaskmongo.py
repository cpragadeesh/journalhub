from doaj.retriever import OJ
from pymongo import MongoClient

conn = MongoClient('localhost:27017')

db = conn.hub   #MongoDB Connection

data = db.data
topiclist = data.find()

topics = []

def fetch(topic, num):
    doaj = 'http://doaj.org/api/v1/'
    query = 'search/articles/'+topic+'?page='+num+'&pageSize=100'
    api = doaj + query
    print api
    D.retriever(api)

def getpages(topic):
    doaj = 'http://doaj.org/api/v1/'
    query = 'search/articles/'+topic+'?page=1&pageSize=100'
    api = doaj + query
    last = D.getlast(api)
    last = last.split('?page=')
    last = last[1].split('&pageSize=')
    return int(last[0])

if __name__ == '__main__':
    
    for topic in topiclist:
        print('\n'+topic['_id']+'\n')
        for prefs in topic['keys']:
            if prefs not in topics:
                print(prefs)
                topics.append(prefs)

    for topic in topics:
        try:
            D = OJ()    #DOAJ

            pagecount = getpages(topic.replace(' ', '%20'))
            
            if pagecount < 5:
                end = pagecount
            
            if pagecount > 5 and pagecount < 20:
                end = int(pagecount/2)

            if pagecount > 20 and pagecount < 100:
                end = int(pagecount/4)

            for c in range(1, end+1):
                if c <= 2:  #Currently fetching only the 1st 2 pages
                    print c
                    fetch(topic.replace(' ', '%20'), str(end))

            # Storing with title as the collection name
            papers = db[topic]
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
            
            del D

        except:
            print 'An error has occurred'
            continue