#!/usr/bin/python

from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import copy
import operator
import logging
from mail import Mail

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

        ##
        self.newset = []
        self.newprefauthorset = []
        self.newprefpubset = []
        self.newprefyearset = []
        ##

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

    def selection(self, pubs, mykeys, exclude):        
        for prefs in mykeys:
            papers = db[prefs]
            paperslist = papers.find()

            for paper in paperslist:
                if paper['_id'] not in exclude:
                    self.titles.append(paper['_id'].encode('utf-8'))
                    self.abstract[paper['_id']] = paper['abstract'].encode('utf-8')
                    self.keywords[paper['_id']] = paper['keywords']
                    self.year[paper['_id']] = paper['year']
                    self.link[paper['_id']] = paper['link']
                    self.headauthor[paper['_id']] = paper['author']
                    self.journalpublisher[paper['_id']] = paper['journal']
                else:
                    continue

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

    ##
    def newkeyset(self, favkey, favkeycount):
        #print '\nTHe New Key Set:\n'
        if favkey is not None and favkeycount is not None:
            if favkeycount > 1:
                for title in self.keywords:
                    if favkey in self.keywords[title]:
                        self.newset.append(favkey)
                    else:
                        continue
            else:
                print 'favkey less than 2'
        else:
            print '\nfavkey is None'

    def prefset(self, favauthor, favauthorcount, favpublisher, favpublishercount, favyear, favyearcount):
        #print '\nThe New Preferred Set:\n'
        if favauthor is not None and favauthorcount is not None:
            if favauthorcount > 1:
                for title in self.headauthor:
                    if favauthor in self.headauthor[title]:
                        self.newprefauthorset.append(title)
                        #print title
                    else:
                        continue
            else:
                print 'favauthorcount less than 2'
        else:
            print '\nfavauthor is None'

        if favpublisher is not None and favpublishercount is not None:
            if favpublishercount > 1:
                for title in self.headauthor:
                    if favpublisher in self.journalpublisher[title]:
                        self.newprefpubset.append(title)
                        #print title
                    else:
                        continue
            else:
                print 'favpublishercount less than 2'
        else:
            print '\nfavpublisher is None'

        if favyear is not None and favyearcount is not None:
            if favyearcount > 1:
                for title in self.headauthor:
                    if favyear in self.year[title]:
                        self.newprefyearset.append(title)
                        #print title
                    else:
                        continue
            else:
                print 'favyearcount less than 2'
        else:
            print '\nfavyear is None'

        #print self.newprefset
    ##

    def crossover(self):
        outputtitles = self.accuracyset[0:2] + self.diversityset[2:5]
        ##
        import random
        if self.newset:
            random.shuffle(self.newset)
            outputtitles = outputtitles + random.sample(self.newset, 1)
            print 'Paper with new key added'
        
        if self.newprefauthorset:
            random.shuffle(self.newprefauthorset)
            outputtitles = outputtitles + random.sample(self.newprefauthorset, 1)
            print 'Paper with preferred author added'

        if self.newprefpubset:
            random.shuffle(self.newprefpubset)
            outputtitles = outputtitles + random.sample(self.newprefpubset, 1)
            print 'Papers with preferred publisher added'

        if self.newprefyearset:
            random.shuffle(self.newprefyearset)
            outputtitles = outputtitles + random.sample(self.newprefyearset, 1)
            print 'Paper with preffered year added'
        ##
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

    def mutation(self, keys, exclude):
        print 'Mutating..'
        
        import random
        random.shuffle(keys)
        key = random.choice(keys)   #Select a random key
        print key
        
        from ccs import CCS
        C = CCS()

        from doaj.retriever import OJ
        D = OJ()
        
        try:
            relkey = C.get_random_sibling(key)
            print relkey  
            #relkey = 'cloud computing'   
        except:
            relkey = ''

        if relkey != '':
            doaj = 'http://doaj.org/api/v1/'
            query = 'search/articles/'+relkey.replace(' ', '%20')+'?page='+'1'+'&pageSize=10'
            api = doaj + query
            print api
            D.retriever(api)
                    
            random.shuffle(D.titles)
            for title in D.titles:
                if title not in exclude:
                    insertJSON = {'title': title,
                        'abstract': D.abstract[title],
                        'keywords': D.keywords[title],
                        'link': D.link[title],
                        'year': D.year[title],
                        'leadauthor': D.author[title],
                        'publisher': D.journal[title]
                    }                    
                    break
            print insertJSON['title']
            self.output.append(insertJSON) 
        
        del D
        #del C     

if __name__ == '__main__':
    
    users = db.users.find()

    for user in users:
        try:
            R = recco()
            print('\n'+user['_id']+'\n')
            email = user['_id']

            topiclist = data.find_one(user['_id'])
            pubslist = publications.find_one(user['_id'])
                
            if pubslist:
                pubs = pubslist['abstracts']            
            else:
                print "Unable to find any publications for user: " + email
                #Using Keys as publications just to generate results
                pubs = topiclist['keys']            

            #fetching all liked and disliked docs to remove from next recco                
            likeddocs = db['likeddocs']
            dislikeddocs = db['dislikeddocs']

            exclude = []

            ldocs = likeddocs.find_one(user['_id'])
            ddocs = dislikeddocs.find_one(user['_id'])

            prefkeys = []
            prefauthor = []
            prefyear = []
            prefpublisher = []

            def most_common(lst):
                if len(lst) == 0:
                    return None
                return max(lst, key = lst.count)
            
            if ldocs and ldocs['papers']:
                for doc in ldocs['papers']:
                    #print doc['title']
                    exclude.append(doc['title'])  
                                
                    for key in doc['keywords']:
                        if key not in topiclist['keys']:
                            prefkeys.append(key)
                        else:
                            continue

                    prefauthor.append(doc['leadauthor'])

                    prefyear.append(doc['year'])

                    prefpublisher.append(doc['publisher'])                
                                
                favkey = most_common(prefkeys)
                favkeycount = prefkeys.count(favkey)
                #print favkey
                #print favkeycount

                favauthor = most_common(prefauthor)
                favauthorcount = prefauthor.count(favauthor)
                #print favauthor
                #print favauthorcount

                favyear = most_common(prefyear)
                favyearcount = prefyear.count(favyear)
                #print favyear
                #print favyearcount

                favpublisher = most_common(prefpublisher)
                favpublishercount = prefpublisher.count(favpublisher)
                #print favpublisher
                #print favpublishercount                     
            else:            
                favkey = None
                favkeycount = None

                favauthor = None
                favauthorcount = None

                favyear = None
                favyearcount = None

                favpublisher = None
                favpublishercount = None
                
                print 'No Liked Docs'        

            if ddocs and ddocs['papers']:
                for doc in ddocs['papers']:
                    #print doc['title']
                    exclude.append(doc['title'])            
            else:
                print 'No Disiked Docs'

            R.selection(pubs, topiclist['keys'], exclude)
            
            R.newkeyset(favkey, favkeycount)
            R.prefset(favauthor, favauthorcount, favpublisher, favpublishercount, favyear, favyearcount)
            
            R.crossover()

            from analyzer.analyzer import analyze
            if ldocs is not None:
                if ldocs['papers']:
                    likes = len(ldocs['papers'])
                else:
                    likes = 0
            else:
                likes = 0

            if ddocs is not None:
                if ddocs['papers']:
                    dislikes = len(ddocs['papers'])
                else:
                    dislikes = 0
            else:
                dislikes = 0

            A = analyze(likes = likes, dislikes = dislikes)

            if A.mutate_or_not():
                R.mutation(topiclist['keys'], exclude)            
            else:
                pass

            del A

            recommendations = db.recco
            recommendations.update_one({'_id':email}, {'$set': {'output':R.output}}, upsert=True)

            mailer = Mail(from_email='journalhub.amrita@gmail.com',
                    to_email=email,                    
                    password="avvp#4321",
                    papers=R.output,
                    smtp_host='smtp.gmail.com')

            mailer.send()

            del R
        
        except:
            print 'An error has occurred'
            continue