from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import copy
import operator
import json
import numpy as np

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

        self.score = None
        self.vector = None
        self.alphababy = {}
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
        docscount, words = self.vector.shape
        self.score = [0] * docscount    #init to 0
        #print(self.score)

    def bestfit(self, c, sett, skip=None):  
        fit = copy.deepcopy(sett)

        index = []
        
        for j in range(c):
            i, value = max(enumerate(fit), key=operator.itemgetter(1))
            if i != skip:
                index.append(i)
            fit[i] = -1

        return index

    def firstset(self, userpubs):
        for k in range(0, len(userpubs)):
            self.score = cosine_similarity(self.vector, self.vector[k])     #Need to do +=
        #Please fix this
        #self.score = self.score / len(userpubs)
        
        index = self.bestfit(20+self.totalUserPubs, self.score, 0)
        del index[:self.totalUserPubs]
        #print(index)
        
        print('\nFirst Set:\n')
        for i in index:
            print('Document: '+self.titles[i])            
            print('Score: %f' % self.score[i])
            self.alphababy[self.titles[i]] = self.score[i]
        
        #print(self.alphababy) 
         
    def worstfit(self, c, sett, skip=None):  
        fit = copy.deepcopy(sett)

        index = []

        for j in range(c):
            i, value = min(enumerate(fit), key=operator.itemgetter(1))
            if i != skip:
                index.append(i)
            fit[i] = 2

        return index

    def secondset(self):
        index = self.worstfit(20, self.score, 0)
        #print(len(index))
        
        print('\nSecond Set:\n')
        for i in index:
            print('Document: '+self.titles[i])            
            print('Score: %f' % self.score[i])
            self.betababy[self.titles[i]] = self.score[i]
        
        #print(self.alphababy)          

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
        self.firstset(pubs)
        self.secondset()

R = recco()
pubs = {'cloud computing is beautifull', 'Phishing is great'}
R.selection(pubs)