import os
import random
import string

import flask
import psycopg2
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

address = "https://localhost:5000/"

app = Flask(__name__, template_folder='html')
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})
app.config["DEBUG"] = True
app.secret_key = os.urandom(24)

def init_database(cur):
    cur.execute("""create table Films (
    	id SERIAL not null,
    	title varchar(30) not null,
    	time integer not null,
    	PRIMARY KEY (id)
    	)""")
    cur.execute("""create table Users (
        	username varchar(20) primary key not null,
        	password varchar(128) not null,
        	sessionID varchar(256)
        	)""")
    cur.execute("""create table Permissions (
        FK_Film integer not null, 
	    FK_User varchar(20) not null, 
	    read boolean not null,
	    write boolean not null,
	    ownership boolean not null,
	    Primary KEY (FK_Film, FK_User),
	    FOREIGN KEY (FK_Film) references Films (id) ON DELETE CASCADE,
	    FOREIGN KEY (FK_User) references Users (username) ON DELETE CASCADE
        )""")
    conn.commit()

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/show-films')
def serve_films():
    return flask.make_response(render_template('showFilms.html'))

@app.route('/delete-film')
def serve_delete_film():
    return flask.make_response(render_template('deleteFilm.html'))

@app.route('/add-film')
def serve_add_film():
    return flask.make_response(render_template('addFilm.html'))

@app.route('/login', methods=['GET','POST'])
def serve_login():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']

        sessionId = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(256))

        return flask.redirect(flask.url_for('serve_account'))
    else:
        return flask.make_response(render_template('login.html'))

@app.route('/register')
def serve_register():
    return flask.make_response(render_template('register.html'))

@app.route('/account')
def serve_account():
    return flask.make_response(render_template('menu.html'))

@app.route('/permissions')
def serve_permissions():
    return flask.make_response(render_template('accessManipulation.html'))

def authorize(username, password):
    cur.execute("SELECT password FROM Users WHERE username = %s;", (username,))
    result = cur.fetchone()
    if result is not None and result[0] == password:
        return 1
    else:
        return 0

@app.route("/users", methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    try:
        cur.execute("INSERT INTO Users VALUES(%s, %s)", (username, password))
        conn.commit()
        return json.dumps({'success': True}), 200, {'ContentType':'application/json'}
    except psycopg2.errors.UniqueViolation:
        return json.dumps({'success': False}), 400, {'ContentType':'application/json'}


@app.route("/login", methods=['GET','POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    sessionId = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(256))

    response = flask.make_response()
    response.status_code =302
    response.set_cookie("sessID", sessionId,httponly=True, secure=True)
    response.location = address + "account"
    return  flask.redirect(flask.url_for('serve_account'))

    cur.execute("SELECT password FROM Users WHERE username = %s;", (username,))
    result = cur.fetchone()
    if result is not None and result[0] == password:
        return response
        #return json.dumps({'success': True, 'ssesId': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(256))}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success': False}), 400, {'ContentType':'application/json'}



'''
@app.route("/setcookie", methods=['GET'])
def setcookie():
    sessionId = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(256))
    response = flask.make_response(render_template('login.html'))
    response.status_code = 200
    response.set_cookie("sessID", sessionId, httponly=True, secure=True)

    return response
'''


@app.route("/films", methods=['GET'])
def get_films():

    print(request.cookies.get("sessID"))
    #username = request.authorization['username']
    #password = request.authorization['password']

    username = request.json['username']
    password = request.json['password']

    if authorize(username, password):
        cur.execute("""SELECT id, title, write, read, ownership FROM Films
        INNER JOIN Permissions ON Films.id = Permissions.FK_Film
        INNER JOIN Users ON Users.username = Permissions.FK_User
        WHERE username = %s""", (username,))
        conn.commit()
        films = cur.fetchall()

        keys = ["id", "title", "write", "read", "ownership"]
        dictionary_list = []
        for film in films:
            dictionary_list.append(dict(zip(keys, film)))

        return json.dumps(dictionary_list)

    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}

@app.route("/film/<int:id>", methods=['GET'])
def get_film(id):
    username = request.authorization['username']
    password = request.authorization['password']

    if authorize(username, password):
        cur.execute("""SELECT read FROM Permissions 
        INNER JOIN Films ON Films.id = Permissions.FK_Film
        INNER JOIN Users ON Users.username = Permissions.FK_User
        WHERE id = %s and username = %s
        """, (id, username))
        result = cur.fetchone()
        if result is not None and result[0] == True:
            cur.execute("SELECT * FROM Films WHERE id = %s;", (id,))

            film = cur.fetchall()[0]
            keys = ["id", "title", "time"]
            return json.dumps(dict(zip(keys, film)))
    return json.dumps({'success': False}), 400, {'ContentType':'application/json'}


@app.route("/films", methods=['POST'])
def set_film():
    title = request.json['title']
    time = request.json['time']
    username = request.authorization['username']
    password = request.authorization['password']
    if authorize(username, password):
        cur.execute("INSERT INTO Films  (title, time) VALUES(%s, %s)", (title, time))
        cur.execute("SELECT id FROM Films ORDER BY id DESC LIMIT 1")
        cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s)",
                    (cur.fetchone()[0], username, True, True, True))
        conn.commit()
        return json.dumps({'success': True}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success': False}), 400, {'ContentType':'application/json'}


@app.route("/films/<int:id>", methods=['PUT'])
def edit_film(id):
    title = request.json['title']
    time = request.json['time']
    username = request.authorization['username']
    password = request.authorization['password']

    if authorize(username, password):
        cur.execute("""SELECT write FROM Permissions 
        INNER JOIN Films ON Films.id = Permissions.FK_Film
        INNER JOIN Users ON Users.username = Permissions.FK_User
        WHERE id = %s and username = %s
        """, (id, username))
        result = cur.fetchone()
        if result is not None and result[0] == True:
            cur.execute("UPDATE Films SET title = %s, time = %s WHERE id = %s", (title, time, id))
            conn.commit()
            return 1
    return 0


@app.route("/films/<int:id>", methods=['DELETE'])
def delete_film(id):
    username = request.authorization['username']
    password = request.authorization['password']

    if authorize(username, password):
        cur.execute("""SELECT write FROM Permissions 
        INNER JOIN Films ON Films.id = Permissions.FK_Film
        INNER JOIN Users ON Users.username = Permissions.FK_User
        WHERE id = %s and username = %s
        """, (id, username))
        result = cur.fetchone()
        if result is not None and result[0] == True:
            cur.execute("DELETE FROM Films WHERE id = %s;", (id,))
            conn.commit()
            return json.dumps({'success': True}), 200, {'ContentType':'application/json'}
    return json.dumps({'success': False}), 400, {'ContentType':'application/json'}

@app.route("/permissions", methods=['POST'])
def set_permissions():
    username = request.authorization['username']
    password = request.authorization['password']
    id = request.json['id']
    username2 = request.json['username2']
    read = request.json['read']
    write = request.json['write']

    if authorize(username, password):
        # Sprawdź czy film należy do użytkownika przekazującego
        cur.execute("""SELECT ownership FROM Permissions 
        INNER JOIN Films ON Films.id = Permissions.FK_Film
        INNER JOIN Users ON Users.username = Permissions.FK_User
        WHERE id = %s and username = %s
        """, (id, username))
        result = cur.fetchone()
        if result is not None and result[0] == True:
            # Sprawdź czy relacja użytkownika z filmem istnieje
            cur.execute("""SELECT * FROM Permissions 
                    WHERE FK_Film = %s and FK_User = %s
                    """, (id, username2))
            result2 = cur.fetchone()
            if result2 is None:
                # Insert
                cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s)",
                            id, username2, read, write, False)

            else:
                # Update
                cur.execute("UPDATE Permissions SET read = %s, write = %s WHERE id = %s", (read, write))
            conn.commit()
            return json.dumps({'success': True}), 200, {'ContentType':'application/json'}
    return json.dumps({'success': False}), 400, {'ContentType':'application/json'}


@app.route("/users", methods=['GET'])
def get_users():

    cur.execute("""SELECT username FROM Users""")
    conn.commit()
    users = cur.fetchall()
    keys = ["username"]
    dictionary_list = []
    for user in users:
        dictionary_list.append(dict(zip(keys, user)))

    return json.dumps(dictionary_list)

# TODO
# transfer ownership



# database connection
try:
    conn = psycopg2.connect(
        dbname='patryk',
        user='patryk',
        host='localhost',
        password='password'
    )
    cur = conn.cursor()
except psycopg2.OperationalError:
    print("No database connection")
    exit()



context = ('cert.pem', 'key.pem')#certificate and key files
app.run(debug=True, ssl_context=context)


cur.close()
conn.close()