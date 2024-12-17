from flask import Flask, request, redirect, url_for, render_template, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your secret key'

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Sujatha#12345',
        database='story_db'
    )
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as e:
    print("Error connecting to MySQL database:", e)
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor.execute('SELECT * FROM Users WHERE User_name = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO Users VALUES (NULL, %s, %s, %s)', (username, email, password))
            conn.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('signup.html', msg=msg)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM Users WHERE User_name = %s AND User_pswd = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['User_id'] = account['User_id']
            session['User_name'] = account['User_name']
            msg = 'Logged in successfully!'
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)

@app.route('/index')
def index():
    return render_template('index.html')


# # Add story route - Displaying the form to add a new story and processing the form submission
# def add_story():
#     if 'loggedin' in session:
#         msg = ''
#         if request.method == 'POST':
#             title = request.form.get('title')
#             story = request.form.get('story')
#             genre = request.form.get('genre')
#             summary = request.form.get('summary')
#             moral = request.form.get('moral')
            
#             if not title or not story or not genre or not summary or not moral:
#                 return render_template("create.html", msg="Please fill in all fields.")

#             user_id = session['User_id']  # Ensure this key is set in the session

#             try:
#                 # Insert data into user_stories table
#                 cursor.execute("INSERT INTO user_stories (title, story, genre, summary, moral, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
#                                (title, story, genre, summary, moral, user_id))
#                 conn.commit()
#                 return redirect(url_for('report'))  # Redirect to report page after successful story addition
#             except Exception as e:
#                 conn.rollback()
#                 print("Error inserting story:", e)
#                 return render_template("create.html", msg="An error occurred. Please try again.")
        
#         return render_template("create.html")  # If GET request, render the create story page
#     else:
#         return redirect(url_for('login'))

@app.route("/add_story", methods=['GET', 'POST'])
def add_story():
    if 'loggedin' in session:
        msg = ''
        if request.method == 'POST' and 'title' in request.form and 'story' in request.form:
            user_id = session['User_id']
            title = request.form['title']
            story = request.form['story']
            genre=request.form['genre']
            summary=request.form['summary']
            moral=request.form['moral']
            print("user_id:", user_id)
            cursor.execute("INSERT INTO user_stories VALUES (NULL,%s,%s, %s,%s,%s,%s)", (title,genre,story,summary,moral,user_id))
            data=cursor.fetchall()
            conn.commit()
            return redirect(url_for('report'))
            # return render_template("report.html",data=data)
        elif request.method == 'GET':
            return render_template("create.html")
            # return redirect('add_story')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('User_id', None)
    session.pop('User_name', None)
    return redirect(url_for('login'))

@app.route('/report')
def report():
    if 'loggedin' in session:
        user_id = session['User_id']
        cursor.execute("SELECT * FROM user_stories WHERE user_id = %s", (user_id,))
        stories = cursor.fetchall()
        return render_template('report.html', data=stories)
    return redirect(url_for('login'))


@app.route('/search')
def search():
    if 'loggedin' in session:
        return render_template("search.html")
    return redirect(url_for('login'))

@app.route('/search_story', methods=['POST'])
def search_story():
    if 'loggedin' in session:
        search_query = request.form.get('search')  # Retrieve the search input
        cursor = conn.cursor(dictionary=True)
        userid = session['User_id']
        
        if search_query:
            cursor.execute('SELECT * FROM user_stories WHERE title LIKE %s AND User_id = %s', 
                           ('%' + search_query + '%', userid))
            value = cursor.fetchall()
            
            if value:
                return render_template('search.html', data=value, search=search_query)
            else:
                msg = "No results found for your search term."
                return render_template('search.html', msg=msg, search=search_query)
        
        # If no search term provided, show the empty form
        return render_template('search.html', search="")
    return redirect(url_for('login'))

# @app.route('/account')
# def account():
#     return render_template("account.html")


@app.route('/view_story/<story_id>')
def view_story(story_id):
    if 'loggedin' in session:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM User_stories WHERE story_id=%s', (story_id,))
            value = cursor.fetchone()
        except mysql.connector.Error as e:
            print("Error", e)
            value = None
        return render_template('view1.html', roll=value)
    return redirect(url_for('login'))


@app.route('/update/<story_id>')
def update(story_id):
    if 'loggedin' in session:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('select * from user_stories where story_id=%s', (story_id,))
        value = cursor.fetchone()
        return render_template('create.html', data=value)
    return redirect(url_for('login'))


@app.route('/update_story', methods=['GET', 'POST'])
def update_story():
    if 'loggedin' in session:
        if request.method == 'POST':
            story_id=request.form['story_id']
            title = request.form['title']
            story = request.form['story']
            genre=request.form['genre']
            summary=request.form['summary']
            moral=request.form['moral']
            cursor.execute("UPDATE user_stories SET title=%s, story=%s, genre=%s ,summary=%s, moral=%s WHERE story_id=%s", 
                           (title, story, genre, summary,moral,story_id))
            conn.commit()
            return redirect(url_for('report'))
    return redirect(url_for('login'))


@app.route('/delete_story/<story_id>', methods=['POST'])
def delete_story(story_id):
    if 'loggedin' in session:
        user_id = session['User_id']
        cursor.execute('SELECT * FROM user_stories WHERE story_id = %s AND User_id = %s', (story_id, user_id))
        story = cursor.fetchone()
        if story:
            cursor.execute('DELETE FROM user_stories WHERE story_id = %s', (story_id,))
            conn.commit()
        else:
            print("Unauthorized delete attempt!")
        return redirect(url_for('report'))
    return redirect(url_for('login'))


@app.route('/account')
def account():
    if 'loggedin' in session:
        return render_template("account.html")
    return redirect(url_for('login'))


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'loggedin' in session:
        if request.method == 'POST':
            user_id = session['User_id'] 
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            cursor.execute('SELECT * FROM users WHERE user_id=%s', (user_id,))
            user=cursor.fetchone()
            print(user)
            if user and user['User_pswd'] == old_password:
                cursor.execute('UPDATE users SET user_pswd = %s WHERE user_id=%s', (new_password, user_id))
                conn.commit()
                return redirect(url_for('login'))
            else:
                conn.close()
                return render_template('account.html', error='Incorrect old password. Please try again.')
        return render_template('account.html')
    return redirect('login')

if __name__ == '__main__':
    app.run(debug=True)

