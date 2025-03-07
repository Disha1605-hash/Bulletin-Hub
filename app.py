from flask import Flask, render_template, request, redirect, url_for, session, url_for, flash
from werkzeug.utils import redirect
from flask_mysqldb import MySQL
from datetime import datetime,timedelta
import MySQLdb.cursors
import re


app = Flask(__name__)
app.secret_key = 'xyzsdfg'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Direction@123'
app.config['MYSQL_DB'] = 'ourproject'

mysql = MySQL(app)

@app.route('/')
def proj():
    return render_template('proj.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    session.pop('username', None) 
    session.pop('WHO', None)  
    session.pop('year', None)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE username = %s AND password = %s', (username, password, ))
        login = cursor.fetchone()
        cursor.close()
        if login:
            session['username'] = True
            session['username'] = login['username']
            session['password'] = login['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT WHO FROM users WHERE username = %s', (login['username'],))
            user_info = cursor.fetchone()
            cursor.execute('SELECT year FROM users WHERE username = %s', (login['username'],))
            year = cursor.fetchone()
            cursor.close()
            session['username'] = username
            session['WHO'] = user_info['WHO'] if user_info else 'Guest'
            session['year'] = year['year'] if user_info else 'Unknown'
            msg = 'Logged in successfully !'
            return render_template('NEW.html', msg=msg, username=login['username'], WHO=session['WHO'], year=session['year'])
        else:
            msg = 'Please enter correct username / password !'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msgs = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            cursor.execute('INSERT INTO register VALUES (% s, % s, % s)', (username, password, email, ))
            cursor.execute('INSERT INTO login VALUES (% s, % s)', (username, password, ))
            mysql.connection.commit()

            cursor.execute('SELECT WHO FROM users WHERE username = %s', (username,))
            user_info = cursor.fetchone()
            cursor.execute('SELECT year FROM users WHERE username = %s', (username,))
            year = cursor.fetchone()
            cursor.close()

            session['username'] = username
            session['WHO'] = user_info['WHO'] if user_info else 'Guest'
            session['year'] = year['year'] if year else 'Unknown'

            msgs = 'You have successfully registered !'
            return render_template('NEW.html', msgs=msgs, username=username, WHO=session['WHO'], year=session['year'])
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msgs = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msgs = 'Username must contain only numbers !'
        elif not username or not password or not email:
            msgs = 'Please fill out the form !'
        else:
            msgs = 'college email id does not exist!'

    elif request.method == 'POST':
        msgs = 'Please fill out the form !'
    return render_template('register.html', msgs=msgs)



@app.route('/NEW')
def NEW():
    username = session.get('username')
    WHO = session.get('WHO')
    year = session.get('year')
    if username:
        return render_template('NEW.html', username=username , WHO=WHO, year=year)
    else:
        return render_template('NEW.html')



@app.route('/about')
def about():
    
    return render_template('about.html')


@app.route('/text')
def text():
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,user, Description, Details, Date FROM notices")
    data = cur.fetchall()
    cur.close()
    return render_template('text.html', notices=data, username=username)


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        cur = mysql.connection.cursor()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT MAX(id) FROM notices")
        max_id = cur.fetchone()[0]
        new_id = max_id + 1 if max_id else 1 
        username = session.get('username')
        Description = request.form['Description']
        Details = request.form['Details']
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("INSERT INTO notices (id, user, Description, Details, Date) VALUES (%s, %s, %s, %s, %s)", (new_id, username, Description, Details, current_date))
        mysql.connection.commit()
        
        cursor.execute('SELECT WHO FROM users WHERE username = %s', (username,))
        user_info = cursor.fetchone()
        cursor.execute('SELECT year FROM users WHERE username = %s', (username,))
        year = cursor.fetchone()
        
        session['username'] = username
        session['WHO'] = user_info['WHO'] if user_info else 'Guest'
        session['year'] = year['year'] if user_info else 'Unknown'
        cur.close()
        return redirect(url_for('text'))  



@app.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    # Assuming user is coming from somewhere, you need to fetch it first
    user = request.args.get('user')
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("SELECT user FROM notices WHERE id=%s", (id,))
    notice_username = cur.fetchone()
    
    if (notice_username and notice_username[0] == user) or (notice_username and notice_username[0] == username):
        flash("Record Has Been Deleted Successfully")
        cur.execute("DELETE FROM notices WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.execute("SELECT id FROM notices")
        notices = cur.fetchall()
        for idx, notice in enumerate(notices, start=1):
            cur.execute("UPDATE notices SET id=%s WHERE id=%s", (idx, notice[0]))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('text'))
    elif (username in ['612203046','612203050']):
        flash("Record Has Been Deleted Successfully")
        cur.execute("DELETE FROM notices WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.execute("SELECT id FROM notices")
        notices = cur.fetchall()
        for idx, notice in enumerate(notices, start=1):
            cur.execute("UPDATE notices SET id=%s WHERE id=%s", (idx, notice[0]))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('text'))
    else:
        flash("You are not authorized to delete this notice.")
        return redirect(url_for('text'))

from flask import render_template

@app.route('/message')
def message():
    id = request.args.get('id')  # Fetch 'id' from request parameters
    cur = mysql.connection.cursor()
    cur.execute("SELECT user FROM notices WHERE id=%s", (id,))
    notice_username = cur.fetchone()
    
    if notice_username:
        username = notice_username[0]
        cur.execute("SELECT WHO, year, email FROM users WHERE username = %s", (username,))
        user_info = cur.fetchone()
        if user_info:
            WHO, year, email = user_info
        else:
            WHO, year, email = 'Guest', 'Unknown', 'Unknown'
    else:
        # Handle the case when notice_username is None
        flash("Notice not found.")
        return redirect(url_for('text'))  # Redirect to a different route or page
    
    mysql.connection.commit()
    cur.close()
    
    return render_template('message.html', id=id, notice_username=username, WHO=WHO, year=year, email=email)


    
if __name__ == "__main__":
    app.run(debug=True)
