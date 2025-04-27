from flask import Flask, render_template, request, redirect, session
import mysql.connector as my
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
con = my.connect(host="localhost", user="root", passwd="Abhijeet@12", database="pro")
cur = con.cursor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        
        sql = "INSERT INTO user(username, password, name) VALUES (%s, %s, %s)"
        val = (username, password, name)
        cur.execute(sql, val)
        con.commit()
        
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        sql = "SELECT password FROM user WHERE username = %s"
        val = (username,)
        cur.execute(sql, val)
        result = cur.fetchone()
        
        if result and result[0] == password:
            session['username'] = username
            return redirect('/quiz')
        else:
            return render_template('login.html', error="Invalid Credentials")
        
    return render_template('login.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    subject = request.args.get('subject', 'cpp')

    sql = f"SELECT * FROM {subject} ORDER BY RAND() LIMIT 5"
    cur.execute(sql)
    questions = cur.fetchall()
    
    if request.method == 'POST':
        score = 0
        for q in questions:
            qid = str(q[0])
            correct = q[6]
            ans = request.form.get(qid)
            if ans == correct:
                score += 1
        
        result1 = f"{subject.upper()} {score}/5"
        current_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "INSERT INTO result(uname, results, datetime) VALUES (%s, %s, %s)"
        val = (username, result1, current_datetime)
        cur.execute(sql, val)
        con.commit()
        
        return redirect('/result')
        
    return render_template('quiz.html', questions=questions, subject=subject)

@app.route('/result')
def result():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    sql = "SELECT * FROM result WHERE uname=%s"
    val = (username,)
    cur.execute(sql, val)
    results = cur.fetchall()
    
    return render_template('result.html', results=results)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
