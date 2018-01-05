class analyze():
    def __init__(self, likes, dislikes):
        self.likes = likes
        self.dislikes = dislikes
        self.total = None
        self.likespercentage = None
        self.dislikespercentage = None

    def compute(self):
        self.total = self.likes + self.dislikes
        if self.total != 0:
            self.likespercentage = self.likes * 100 / self.total
        else:
            self.likespercentage = 0
            pass
            
        if self.total != 0:
            self.dislikespercentage = self.dislikes * 100 / self.total
        else:
            self.dislikespercentage = 0
            pass

    def mutate_or_not(self):
        self.compute()
        
        if self.likespercentage < 70:
            return True
        else:
            return False

    

if __name__ == '__main__':
    from pymongo import MongoClient

    conn = MongoClient('localhost:27017')
    db = conn.hub   #MongoDB Connection

    users = db.users.find()
    for user in users:
        print user['_id']

        likeddocs = db['likeddocs']
        dislikeddocs = db['dislikeddocs']

        ldocs = likeddocs.find_one(user['_id'])
        ddocs = dislikeddocs.find_one(user['_id'])

        A = analyze(likes = len(ldocs['papers']), dislikes = len(ddocs['papers']))
        print 'Likes Percentage: %d' % A.likespercentage
        print 'Dislikes Percentage: %d' % A.dislikespercentage

        del A