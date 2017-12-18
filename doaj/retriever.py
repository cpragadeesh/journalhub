import urllib.request
import json
import requests

class OJ:
    def __init__(self):
        self.titles = []
        self.abstract = {}
        self.year = {}
        self.keywords = {}
        #self.journal = {}
        #self.author = {}
        self.link = {}

    def retriever(self, api):
        
        with urllib.request.urlopen(api) as url:
            data = json.loads(url.read().decode('utf-8'))
            results = data['results']

        last = data['last']
        print(last)

        for result in results:
            try:
                bibjson = result['bibjson']

                title = str(bibjson['title'].encode('utf-8'))
                self.titles.append(title)
                self.link[title] = bibjson['link']
                self.abstract[title] = str(bibjson['abstract'].encode('utf-8'))

                #self.journal = bibjson['journal']                
                #self.author = bibjson['author']

                self.year[title] = bibjson['year']
                self.keywords[title] = []
                
                for key in bibjson['keywords']:
                    self.keywords[title].append(str(key.encode('utf-8')))

            except:
                continue

        #with open('abstract.json', 'w') as outfile:
            #json.dump(self.abstract, outfile)

if __name__ == '__main__':
    doaj = 'http://doaj.org/api/v1/'
    query = 'search/articles/cloud%20computing?page=1&pageSize=100&sort=year%3Adesc'
    api = doaj + query
    D = OJ()
    D.retriever(api)