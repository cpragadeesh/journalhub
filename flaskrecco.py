from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import copy
import operator

conn = MongoClient('localhost:27017')

db = conn.hub   #MongoDB Connection

data = db.data
topiclist = data.find()

publications = db.pubs

class recco():
    def __init__(self):
        self.titles = []
        self.abstract = {}
        self.keywords = {}
        self.year = {}
        self.link = {}
        self.headauthor = {}
        self.journalpublisher = {}

        self.score = None
        self.vector = None
        self.alphababy = {}
        self.betababy = {}
        self.accuracyset = []
        self.diversityset = []
        self.output = []
        
        self.totalUserPubs = 0

    def prerequisite(self, userAbstracts):
        docs = []
        for abstract in userAbstracts:
            docs.append(abstract)
            self.totalUserPubs = self.totalUserPubs + 1

        for a in self.abstract:
            docs.append(self.abstract[a])

        vectorizer = TfidfVectorizer(stop_words='english', use_idf=True,  ngram_range=(1, 2))
        self.vector = vectorizer.fit_transform(docs)
        print("No. of Documents: %d, No. of Unique Words: %d" % self.vector.shape)
        docscount, words = self.vector.shape
        self.score = [0] * docscount    #init to 0
        #print(self.score)

    def bestfit(self, c, sett, skip=None):  
        fit = copy.deepcopy(sett)

        index = []
        
        for j in range(c):
            i, value = max(enumerate(fit), key=operator.itemgetter(1))
            if i not in skip:
                index.append(i)
            fit[i] = -1

        return index

    def firstset(self, userpubs):
        for k in range(len(userpubs)):
            tmp = cosine_similarity(self.vector, self.vector[k])
            self.score = list(map(operator.add, self.score, tmp))
        
        #self.score = self.score / len(userpubs)
        #Need to divide

        del self.score[:self.totalUserPubs]
        #print(self.score)
        
        index = self.bestfit(20+self.totalUserPubs, self.score, [])
        #print(index)
        
        print('\nFirst Set:\n')
        for i in index:
            print('Document: '+self.titles[i])            
            print('Score: %f' % self.score[i])
            self.alphababy[self.titles[i]] = self.score[i]
        
        #print(self.alphababy) 
         
    def worstfit(self, c, sett, skip=[]):  
        fit = copy.deepcopy(sett)

        index = []

        for j in range(c):
            i, value = min(enumerate(fit), key=operator.itemgetter(1))
            if i not in skip:
                index.append(i)
            fit[i] = 2

        return index

    def secondset(self):
        index = self.worstfit(20, self.score)
        #print(len(index))
        
        print('\nSecond Set:\n')
        for i in index:
            print('Document: '+self.titles[i])            
            print('Score: %f' % self.score[i])
            self.betababy[self.titles[i]] = self.score[i]
        
        #print(self.alphababy)          

    def selection(self, pubs, mykeys):        
        for prefs in mykeys:
            papers = db[prefs]
            paperslist = papers.find()

            for paper in paperslist:
                self.titles.append(paper['_id'])
                self.abstract[paper['_id']] = paper['abstract']
                self.keywords[paper['_id']] = paper['keywords']
                self.year[paper['_id']] = paper['year']
                self.link[paper['_id']] = paper['link']
                self.headauthor[paper['_id']] = paper['author']
                self.journalpublisher[paper['_id']] = paper['journal']

        print('Selected '+ str(len(self.link)) +' links')
        print('Selected '+ str(len(pubs)) +' user publications')
        self.prerequisite(pubs)
        self.firstset(pubs)
        self.secondset()

        #Top 5 of both sets randomly
        #Accuracy Set
        for paper in self.alphababy:
            self.accuracyset.append(paper)

        self.accuracyset = self.accuracyset[0:5]
        print('\nAccuracy Set')
        print(self.accuracyset)

        #Diversity Set
        for paper in self.betababy:
            self.diversityset.append(paper)

        self.diversityset = self.diversityset[0:5]
        print('\nDiversity Set')
        print(self.diversityset)

#pubs = {'cloud computing is beautifull', 'Phishing is great'}

users = db.users.find()

for user in users:
    R = recco()
    print('\n'+user['_id']+'\n')

    topiclist = data.find_one(user['_id'])
    pubslist = publications.find_one(user['_id'])
    pubs = pubslist['abstracts']

    R.selection(pubs, topiclist['keys'])
    del R