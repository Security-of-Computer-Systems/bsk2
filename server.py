import os
import random
import string

import flask
import networkx as nx
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

# delegation graphs
delegation_graph = nx.DiGraph()
read_graph = nx.DiGraph()
write_graph = nx.DiGraph()

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
	    delegation boolean not null,
	    Primary KEY (FK_Film, FK_User),
	    FOREIGN KEY (FK_Film) references Films (id) ON DELETE CASCADE,
	    FOREIGN KEY (FK_User) references Users (username) ON DELETE CASCADE
        )""")
    conn.commit()

    # Create users
    letters = string.ascii_letters
    cur.execute("INSERT INTO Users VALUES(%s, %s)",
                ("abacki", ''.join(random.choice(letters) for i in range(126))))
    cur.execute("INSERT INTO Users VALUES(%s, %s)",
                ("babacki", ''.join(random.choice(letters) for i in range(126))))
    cur.execute("INSERT INTO Users VALUES(%s, %s)",
                ("cabacki", ''.join(random.choice(letters) for i in range(126))))

    # Create films
    cur.execute("INSERT INTO Films (title, time) VALUES(%s, %s)",
                ("Nietykalni", 112))
    cur.execute("INSERT INTO Films (title, time) VALUES(%s, %s)",
                ("Zielona mila", 188))
    cur.execute("INSERT INTO Films (title, time) VALUES(%s, %s)",
                ("Ojciec Chrzestny", 175))

    conn.commit()

    # Create permissions
    cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s, %s)",
                (1, "abacki", True, True, True, True))
    cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s, %s)",
                (2, "babacki", True, True, True, True))
    cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s, %s)",
                (3, "cabacki", True, True, True, True))
    cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s, %s)",
                (1, "babacki", True, True, False, True))
    cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s, %s)",
                (3, "babacki", True, True, False, False))

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

@app.route('/add-film', methods=['GET','POST'])
def serve_add_film():
    if request.method == "POST":

        sessionID = request.cookies.get("sessID")

        cur.execute("""
        SELECT username 
        FROM Users 
        WHERE sessionID = %s""",(sessionID,))

        username = cur.fetchone()

        if username is not None:
            title = request.form.get("title")
            time = request.form.get("time")

            cur.execute("INSERT INTO Films  (title, time) VALUES(%s, %s)", (title, time,))
            cur.execute("SELECT id FROM Films ORDER BY id DESC LIMIT 1")
            cur.execute("INSERT INTO Permissions VALUES(%s,%s, %s, %s, %s, %s)",
                        (cur.fetchone(),username, True, True, True, True))
            conn.commit()

            return flask.redirect(flask.url_for("serve_add_film"))
        else:
            return flask.redirect(flask.url_for("serve_add_film"))

    else:
        return flask.make_response(render_template('addFilm.html'))

@app.route('/login', methods=['GET','POST'])
def serve_login():
    if request.method=="POST":
        username = request.form.get("login")
        password = request.form.get("password")

        cur.execute("SELECT password FROM Users WHERE username = %s;", (username,))
        result = cur.fetchone()
        if result is not None and result[0] == password:
            sessionId = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(256))

            cur.execute("UPDATE Users "
                        "SET sessionID = %s"
                        "WHERE username = %s;", (sessionId,username,))

            conn.commit()

            response = flask.make_response()
            response.status_code = 302
            response.set_cookie("sessID", sessionId, httponly=True, secure=True)
            response.location = address + "account"

            return response

        else:
            return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    else:
        return flask.make_response(render_template('login.html'))

@app.route('/register', methods=['GET','POST'])
def serve_register():
    if request.method=='POST':
        username = request.form.get("login")
        password = request.form.get("password")

        try:
            cur.execute("INSERT INTO Users (username, password) VALUES(%s, %s)", (username, password,))
            conn.commit()
            return flask.make_response(render_template('login.html'))
        except psycopg2.errors.UniqueViolation:
            return flask.make_response(render_template('register.html'))
    else:
        return flask.make_response(render_template('register.html'))

@app.route('/account')
def serve_account():
    return flask.make_response(render_template('menu.html'))

@app.route('/permissions')
def serve_permissions():
    return flask.make_response(render_template('accessManipulation.html'))

@app.route("/films", methods=['GET'])
def get_films():

    sessionID = request.cookies.get("sessID")

    cur.execute("""SELECT id, title, write, read, ownership, delegation FROM 
                (SELECT FK_Film, write, read, ownership, delegation FROM Permissions
                INNER JOIN Users ON Users.username = Permissions.FK_User
                WHERE sessionID = %s) as user_permissions RIGHT JOIN Films on user_permissions.FK_Film = Films.id
                """, (sessionID,))

    conn.commit()
    films = cur.fetchall()
    keys = ["id","title", "write", "read","delegation", "ownership" ]
    dictionary_list = []
    for film in films:
        dictionary_list.append(dict(zip(keys, film)))

    return json.dumps(dictionary_list)

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

# Elimination of cycles in the permission delegation graph
# Disability of granting permission to the same object by more than one donor
def can_delegate(edge, delegation, read, write):

    if delegation:
        tmp_graph = delegation_graph
        tmp_graph.add_edge(edge[0], edge[1])
        # check if graph has cycles
        for cycle in nx.simple_cycles(tmp_graph):
            return False
        if len([n for n in tmp_graph.predecessors(edge[1])]) >= 2:
            return False
    if read:
        tmp_graph = read_graph
        tmp_graph.add_edge(edge[0], edge[1])
        # check if graph has cycles
        for cycle in nx.simple_cycles(tmp_graph):
            return False
        if len([n for n in tmp_graph.predecessors(edge[1])]) >= 2:
            return False
    if write:
        tmp_graph = write_graph
        tmp_graph.add_edge(edge[0], edge[1])
        # check if graph has cycles
        for cycle in nx.simple_cycles(tmp_graph):
            return False
        if len([n for n in tmp_graph.predecessors(edge[1])]) >= 2:
            return False

    if delegation:
        delegation_graph.add_edge(edge[0], edge[1])
    if read:
        read_graph.add_edge(edge[0], edge[1])
    if write:
        write_graph.add_edge(edge[0], edge[1])
    return True

@app.route("/permissions", methods=['POST'])
def set_permissions():
    sessionID = request.cookies.get("sessID")
    id = request.json['id']
    username2 = request.json['username2']
    read = request.json['read']
    write = request.json['write']
    delegation = request.json['delegation']

    # find donor user's username
    cur.execute("""SELECT username FROM Users  
        WHERE sessionID = %s
        """, (sessionID))
    donor_username = cur.fetchone()[0]


    cur.execute("""SELECT delegation, read, write FROM Permissions 
    INNER JOIN Films ON Films.id = Permissions.FK_Film
    INNER JOIN Users ON Users.username = Permissions.FK_User
    WHERE id = %s and sessionID = %s
    """, (id, sessionID))
    result = cur.fetchone()

    #  Check if user has delegation permission, assigned permissions,
    if result is not None and result[0] == True and (read <= result[1]) and (write <= result[2]):
        # Elimination of cycles in the permission delegation graph
        # Disability of granting permission to the same object by more than one donor
        if can_delegate((donor_username, username2), delegation, read, write):

            # Sprawdź czy relacja użytkownika z filmem istnieje
            cur.execute("""SELECT * FROM Permissions 
                    WHERE FK_Film = %s and FK_User = %s
                    """, (id, username2))
            result2 = cur.fetchone()
            if result2 is None:
                # Insert
                cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s)",
                            id, username2, read, write, False, delegation)

            else:
                # Update
                cur.execute("UPDATE Permissions SET read = %s, write = %s WHERE id = %s", (read, write, delegation))
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

@app.route("/permissions", methods=['POST'])
def transfer_ownership():
    id = request.json['id']
    username2 = request.json['username2']
    read = request.json['read']
    write = request.json['write']
    delegation = request.json['delegation']
    sessionID = request.cookies.get("sessID")

    # Check if user is owner, and has assigned permissions
    cur.execute("""SELECT ownership, delegation, read, write FROM Permissions 
    INNER JOIN Films ON Films.id = Permissions.FK_Film
    INNER JOIN Users ON Users.username = Permissions.FK_User
    WHERE id = %s and sessionID = %s
    """, (id, sessionID))
    result = cur.fetchone()
    if result is not None and result[0] == True and (delegation <= result[1]) and (read <= result[2]) and (write <= result[3]):

        # Check if there is relation between user and film (insert if not, update if yes)
        cur.execute("""SELECT * FROM Permissions WHERE FK_Film = %s and FK_User = %s""", (id, username2))
        result2 = cur.fetchone()
        if result2 is None:
            # Insert
            cur.execute("INSERT INTO Permissions VALUES(%s, %s, %s, %s, %s, %s)",
                        id, username2, read, write, True, delegation)
        else:
            # Update
            cur.execute("UPDATE Permissions SET read = %s, write = %s, delegation = %s, ownership = %s WHERE id = %s",
                        (read, write, delegation, True))
        # removing permissions of donor
        cur.execute("UPDATE Permissions SET read = %s, write = %s, delegation = %s, ownership = %s WHERE id = %s",
                    (False, False, False, False))
        conn.commit()
        return json.dumps({'success': True}), 200, {'ContentType':'application/json'}
    return json.dumps({'success': True}), 400, {'ContentType': 'application/json'}


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



#certificate and key files
context = ('cert.pem', 'key.pem')

app.run(debug=True, ssl_context=context)


cur.close()
conn.close()