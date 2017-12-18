import urllib.request
import feedparser

#Refer this link - https://arxiv.org/help/api/user-manual
class extract_from_arxiv:
# This module extracts research papers from the arxiv website
    def __init__(self):
        self.titles = []
        self.publish_year = []
        self.abstracts = []
        self.links = []
        self.year = "" # I use this to extract the first 4 characters from published date (year)

    def retrieve(self, complete_url):
        
        with urllib.request.urlopen(complete_url) as c_url:
            data = c_url.read()

        feed = feedparser.parse(data)
        
        for entry in feed.entries:
            self.titles.append(entry.title)
            self.year = entry.published
            self.publish_year.append(self.year[0:4])
            self.year = "" # Destroy the previous value of year
            self.abstracts.append(entry.summary)
            for link in entry.links:
                if "title" in link:
                    self.links.append(link.href)

        #print(self.publish_year)

if __name__ == '__main__':

    url = 'http://export.arxiv.org/api/'
    #Modify the below query as per requirements
    #You can retrieve maximum 2000 papers at a time. I have set it at 1500.
    query = 'query?search_query=ti:cloud%20computing+OR+abs:cloud%20computing&start=0&max_results=1500&sortBy=lastUpdatedDate&sortOrder=descending'
    full_url = url + query
    e = extract_from_arxiv()
    e.retrieve(full_url)