import psycopg2
import json
from flask import Flask, request

app = Flask(__name__)
app.config["DEBUG"] = True

def init_database(cur):
    cur.execute("""create table Films (
    	id SERIAL ,
    	title varchar(30),
    	time integer,
    	PRIMARY KEY (id)
    	)""")
    cur.execute("""create table Users (
        	username varchar(20) primary key,
        	password varchar(20)
        	)""")
    cur.execute("""create table Permissions (
        FK_Film integer, 
	    FK_User varchar(20), 
	    read boolean,
	    write boolean,
	    ownership boolean,
	    Primary KEY (FK_Film, FK_User),
	    FOREIGN KEY (FK_Film) references Films (id) ON DELETE CASCADE,
	    FOREIGN KEY (FK_User) references Users (username) ON DELETE CASCADE
        )""")

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


@app.route("/login", methods=['GET'])
def login():
    username = request.authorization['username']
    password = request.authorization['password']

    cur.execute("SELECT password FROM Users WHERE username = %s;", (username,))
    result = cur.fetchone()
    if result is not None and result[0] == password:
        return json.dumps({'success': True}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success': False}), 400, {'ContentType':'application/json'}


@app.route("/films", methods=['GET'])
def get_films():
    username = request.authorization['username']
    password = request.authorization['password']

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

    return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

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


# TODO
# transfer ownership
# get users


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



app.run()

cur.close()
conn.close()