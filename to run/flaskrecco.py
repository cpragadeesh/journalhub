#!/usr/bin/python

from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import copy
import operator
import logging

logging.basicConfig(filename="recco.log", 
    level=logging.DEBUG,
    format='%(asctime)s %(message)s')

logging.debug("Starting script")
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
        count = 0

        while (count <= c):
            i, value = min(enumerate(fit), key=operator.itemgetter(1))
            if i > 0.000000:
                index.append(i)
                count = count + 1
            fit[i] = 2*self.totalUserPubs

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
                self.titles.append(paper['_id'].encode('utf-8'))
                self.abstract[paper['_id']] = paper['abstract'].encode('utf-8')
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

    def crossover(self):
        outputtitles = self.accuracyset[0:2] + self.diversityset[2:5]
        print('\nOutput')
        for paper in outputtitles:
            try:
                title = paper
                abstract = self.abstract[title]
                keywords = self.keywords[title]
                year = self.year[title]
                link = self.link[title]
                author = self.headauthor[title]
                publisher = self.journalpublisher[title]

                insertJSON = {'title':title, 'abstract':abstract, 'keywords':keywords, 'year':year,
                    'link':link, 'leadauthor':author, 'publisher':publisher}

                self.output.append(insertJSON)
            except Exception:
                continue

        for paper in self.output:
            try:
                print(paper['title'])
                print(paper['abstract']+'\n\n')
            except Exception:
                continue   


#pubs = {'cloud computing is beautifull', 'Phishing is great'}

users = db.users.find()

for user in users:
    R = recco()
    print('\n'+user['_id']+'\n')
    email = user['_id']

    topiclist = data.find_one(user['_id'])
    pubslist = publications.find_one(user['_id'])
        
    if not pubslist:
        print "Unable to find any publications for user: " + email
        continue
    
    pubs = pubslist['abstracts']

    R.selection(pubs, topiclist['keys'])
    R.crossover()

    recommendations = db.recco
    recommendations.update_one({'_id':email}, {'$set': {'output':R.output}}, upsert=True)

    listofpapers = ''#R.output[0]['title']+'\nLink: '+'http://journalhub.pragadeesh.com/'+email+'/'+str(R.output[0]['title'].replace(' ', '+'))+'/\n\n'+ \
     #   R.output[1]['title']+'\nLink: '+'http://journalhub.pragadeesh.com/'+email+'/'+str(R.output[1]['title'].replace(' ', '+'))+'/\n\n'+ \
     #   R.output[2]['title']+'\nLink: '+'http://journalhub.pragadeesh.com/'+email+'/'+str(R.output[2]['title'].replace(' ', '+'))+'/\n\n'+ \
     #   R.output[3]['title']+'\nLink: '+'http://journalhub.pragadeesh.com/'+email+'/'+str(R.output[3]['title'].replace(' ', '+'))+'/\n\n'+ \
     #   R.output[4]['title']+'\nLink: '+'http://journalhub.pragadeesh.com/'+email+'/'+str(R.output[4]['title'].replace(' ', '+'))+'/\n';

    import smtplib

    logging.debug("Sending email to " + email)

    fromaddr = 'journalhub.amrita@gmail.com'
    to = email
    message = 'Welcome, \nYour weekly recommendation is ready to be viewed in the below given link.\nhttp://journalhub.pragadeesh.com/'+email+'\n\n'+ \
        listofpapers+'\nRegards,\nJournal Hub Team';
    password = 'avvp#4321'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(fromaddr, password)
    server.sendmail(fromaddr, to, message)
    logging.debug("Email sent.")
    server.quit()

    del R