from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import copy
import operator
import json

conn = MongoClient('mongodb://venkat:mongo@DESKTOP-B9O8E12:27017/hub')

db = conn.hub   #MongoDB Connection

topics = db.topics
topiclist = topics.find()

class recco():
    def __init__(self):
        self.titles = []
        self.abstract = {}
        self.keywords = {}
        self.year = {}
        self.link = {}

        self.score = {}
        self.vector = None
        self.alphababy = []
        self.betababy = []
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

    def selection(self, pubs):
        for topic in topiclist:    
            papers = db[topic['topic']]
            paperslist = papers.find()
            for paper in paperslist:
                self.titles.append(paper['title'])
                self.abstract[paper['title']] = paper['abstract']
                self.keywords[paper['title']] = paper['keywords']
                self.year[paper['title']] = paper['year']
                self.link[paper['title']] = paper['link']

        print('Selected '+ str(len(R.link)) +' links')
        print('Selected '+ str(len(pubs)) +' user publications')
        self.prerequisite(pubs)

R = recco()
pubs = {'cloud computing is beautifull', 'Phishing is great'}
R.selection(pubs)