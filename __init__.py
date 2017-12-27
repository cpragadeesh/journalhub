from flask import Flask, flash, render_template, request, session
from pymongo import MongoClient

conn = MongoClient('localhost:27017')

db = conn.hub

app = Flask(__name__)
app.secret_key = '#4321'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/newuser')
def newuser():
   return render_template('user.html')

@app.route('/add', methods = ['POST', 'GET'])
def add():
    if request.method == 'POST':
        try:
            name = request.form['name']
            age = request.form['age']
            phone = request.form['phone']
            email = request.form['email']
            password = request.form['password']
         
            users = db['users']
            insertJSON = {'_id':email, 'pass':password, 'name':name, 'age':age, 'phone':phone}
            users.insert_one(insertJSON)
            msg = 'Welcome '+insertJSON['name']

            return render_template('result.html', msg = msg)
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
   
    return render_template('profile.html', rows = rows)

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
            
            return render_template('profile.html', rows = rows)

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

    if request.method == 'POST':
        keywords = request.form['keywords'].split('#')
        keywords.pop(len(keywords)-1)        

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

@app.route('/<string:email>', methods=['GET', 'POST'])
def fetchpaper(email):
    #if session['email'] == email:
    recco = db['recco']
    rows = recco.find_one({'_id': email}, {'output':1}) 

    return render_template('output.html', rows = rows['output'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)