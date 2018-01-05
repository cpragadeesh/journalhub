from flask import Flask, flash, render_template, request, session
from pymongo import MongoClient
import urllib

conn = MongoClient('localhost:27017')

db = conn.hub

app = Flask(__name__)
app.secret_key = '#4321'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/like')
def like():
    userid = request.args.get('userid')
    paperid = request.args.get('paperid')

    userid = urllib.unquote(userid).decode('utf8')
    paperid = urllib.unquote(paperid).decode('utf8')

    #TODO store in db
    recco = db['recco']
    rows = recco.find_one({'_id': userid}, {'output':1}) 

    paper = ''
    for row in rows['output']:
        if row['title'] == paperid:
            paper = row
        else:
            continue

    #Separately storing all the papers each user liked for viewing it later
    likeddocs = db['likeddocs']
    likeddocs.update_one({'_id':userid}, {'$addToSet':{
        'papers':{'title':paper['title'],
        'abstract':paper['abstract'],
        'keywords':paper['keywords'],
        'link':paper['link'],
        'leadauthor':paper['leadauthor'],
        'year':paper['year'],
        'publisher':paper['publisher']}
    }}, upsert=True)

    #Removing from disliked if user accidentally disliked it
    dislikeddocs = db['dislikeddocs']
    dislikeddocs.update_one({'_id':userid}, {'$pull':{
        'papers':{'title':paper['title'],
        'abstract':paper['abstract'],
        'keywords':paper['keywords'],
        'link':paper['link'],
        'leadauthor':paper['leadauthor'],
        'year':paper['year'],
        'publisher':paper['publisher']}
    }}, upsert=False)
    #Done

    return "Like processed " + userid + " " + paperid

@app.route('/dislike')
def dislike():
    userid = request.args.get('userid')
    paperid = request.args.get('paperid')
    
    userid = urllib.unquote(userid).decode('utf8')
    paperid = urllib.unquote(paperid).decode('utf8')
        
    #TODO store in db 
    recco = db['recco']
    rows = recco.find_one({'_id': userid}, {'output':1}) 

    paper = ''
    for row in rows['output']:
        if row['title'] == paperid:
            paper = row
        else:
            continue

    #Separately storing all the papers each user disliked for viewing it later
    dislikeddocs = db['dislikeddocs']
    dislikeddocs.update_one({'_id':userid}, {'$addToSet':{
        'papers':{'title':paper['title'],
        'abstract':paper['abstract'],
        'keywords':paper['keywords'],
        'link':paper['link'],
        'leadauthor':paper['leadauthor'],
        'year':paper['year'],
        'publisher':paper['publisher']}
    }}, upsert=True)

    #Removing from liked if user accidentally liked it
    likeddocs = db['likeddocs']
    likeddocs.update_one({'_id':userid}, {'$pull':{
        'papers':{'title':paper['title'],
        'abstract':paper['abstract'],
        'keywords':paper['keywords'],
        'link':paper['link'],
        'leadauthor':paper['leadauthor'],
        'year':paper['year'],
        'publisher':paper['publisher']}
    }}, upsert=False)
    #DONE

    return "Dislike processed " + userid + " " + paperid

@app.route('/newuser')
def newuser():
   return render_template('user.html')

@app.route('/add', methods = ['POST', 'GET'])
def add():
    if request.method == 'POST':
        try:
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']
            password = request.form['password']
         
            users = db['users']
            insertJSON = {'_id':email, 'pass':password, 'name':name, 'phone':phone}
            users.insert_one(insertJSON)
            msg = 'Welcome '+insertJSON['name']

            return render_template('data.html', msg = msg)
        except:
            msg = 'Error: Unable to Register User'
            return render_template('home.html', msg = msg)

        finally:
            session['logged_in'] = True
            session['email'] = email        

@app.route('/profile')
def profile():
    users = db['users']   
    email = session['email']
    rows = users.find_one({'_id': email}, {'_id':1, 'name':1, 'age':1, 'phone':1})

    likeddocs = db['likeddocs']
    likes = likeddocs.find_one({'_id': email})
    if likes is None:
        likes = {'papers':''}

    dislikeddocs = db['dislikeddocs']
    dislikes = dislikeddocs.find_one({'_id': email})
    if dislikes is None:
        dislikes = {'papers':''}

    data = db['data']
    keys = data.find_one({'_id': email}, {'keys':1})
    if keys is None:
        keys = {'keys':''}

    folder = db['pubs']
    pubs = folder.find_one({'_id': email}, {'abstracts':1})
    if pubs is None:
        pubs = {'abstracts':''}

    from to_run.analyzer.analyzer import analyze

    A = analyze(likes = len(likes['papers']), dislikes = len(dislikes['papers']))
    A.compute()

    statistics = {'Total Papers Seen': A.total,
        'Percentage of Papers Liked': A.likespercentage,
        'Percentage of Papers Disiked': A.dislikespercentage}
   
    return render_template('profile.html', stats = statistics, rows = rows, likes = likes['papers'], 
        keys = keys['keys'], pubs = pubs['abstracts'], dislikes = dislikes['papers'])

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def check():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = db['users']
        rows = users.find_one({'_id': email, 'pass':password}, {'_id':1, 'name':1, 'age':1, 'phone':1}) 

        if rows != None:
            session['logged_in'] = True
            session['email'] = email
            
            return render_template('data.html', rows = rows)

        else:
            error = 'Username Not Found'   
            return render_template('home.html', error=error)

@app.route('/userdata')
def data():
    if session['logged_in'] and session['email'] != '':
        return render_template('data.html')
    else:
        return render_template('home.html')

@app.route('/pushkeys', methods = ['POST', 'GET'])
def keys():
    data = db['data']
    
    email = session['email']

    import string

    if request.method == 'POST':
        words = request.form['keywords'].split(',')
        keywords = []
        for key in words:
            key = key.strip() 
            keywords.append(key)

        data.update_one({'_id':email}, {'$set': {'keys':keywords}}, upsert=True)

    return render_template('data.html')

@app.route('/pushpubs', methods = ['POST', 'GET'])
def pubs():
    folder = db['pubs']
    
    email = session['email']

    if request.method == 'POST':
        abstracts = request.form['abstracts'].split('##overendl##')
        a = filter(lambda a: a != "", abstracts)
                
        keywords = request.form['keywords']

        folder.update_one({'_id':email}, {'$set': {'abstracts':a}}, upsert=True)

    return render_template('data.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html')

@app.route('/<string:email>/<string:id>', methods=['GET', 'POST'])
def fetchpaper(email, id):
    #if session['email'] == email:
    recco = db['recco']
    rows = recco.find_one({'_id': email}, {'output':1}) 

    paper = ''
    for row in rows['output']:
        if row['title'] == id:
            paper = row
        else:
            continue
    
    return render_template('paper.html', rows = paper)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)