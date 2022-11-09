"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
# accessible as a variable in index.html:
import flask
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import flask_login
from datetime import datetime

from backend import user_resource, photo_resource, album_resource, general_resource

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'super secret string'  # Change this!

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://xg2399:4028@34.75.94.195/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

users = engine.execute("SELECT email from Users").fetchall()


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback;
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route("/friend", methods=['GET', 'POST'])
@flask_login.login_required
def searchfriend():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        hometown = request.form.get('hometown')
        if email and first_name and last_name:
            search = g.conn.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE email = '{0}'"
                "AND first_name='{1}' AND last_name ='{2}'".format(email, first_name, last_name)).fetchall()
        elif first_name and last_name:
            search = g.conn.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE first_name "
                "='{first_name}' AND last_name ='{last_name}'".format(first_name=first_name,
                                                                      last_name=last_name)).fetchall()
        elif first_name:
            search = g.conn.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE first_name "
                "='{first_name}'".format(first_name=first_name)).fetchall()
        elif last_name:
            search = g.conn.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE last_name "
                "='{last_name}'".format(last_name=last_name)).fetchall()
        elif email:
            search = g.conn.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE email = '{0}'"
                .format(email)).fetchall()
        elif hometown:
            search = g.conn.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE hometown = '{0}'".format(
                    hometown)).fetchall()
        searchlist = []
        if search:
            for temp in search:
                if temp[2] != 'anonymous@bu.edu':
                    searchlist.append(temp)
        recommand = user_resource.getRecommandFriend(uid)
        friendlist = user_resource.getUserFriend(uid)
        if searchlist:
            return render_template('friend.html', searchlist=searchlist, recommand=recommand, friendlist=friendlist)
        else:
            return render_template('friend.html', searchlist=None, recommand=recommand, friendlist=friendlist)
    else:
        uid = user_resource.getUserIdFromEmail(flask_login.current_user.id)
        friendlist = user_resource.getUserFriend(uid)
        recommand = user_resource.getRecommandFriend(uid)
        return render_template('friend.html', friendlist=friendlist, recommand=recommand)


@app.route("/addfriend", methods=['GET'])
@flask_login.login_required
def addfriend():
    if request.method == 'GET':
        femail = request.args.get('femail')
        if femail is None:
            message = "None"
            return render_template('addfriend.html', message=message)
        fuid = user_resource.getUserIdFromEmail(femail)
        uid = user_resource.getUserIdFromEmail(flask_login.current_user.id)
        DOF = datetime.today().strftime('%Y-%m-%d')
        count = len(
            g.conn.execute("SELECT * FROM Is_Friend WHERE uid ='{0}' AND fuid = '{1}'".format(uid, fuid)).fetchall())
        if fuid == uid:
            message = "Same"
        elif count == 0:
            message = "True"
            g.conn.execute('''INSERT INTO Is_Friend (date, fuid, uid) VALUES (%s, %s, %s )''', (DOF, fuid, uid))
            g.conn.execute('''INSERT INTO Is_Friend (date, fuid, uid) VALUES (%s, %s, %s )''', (DOF, uid, fuid))
            # conn.commit()
        elif count == 1:
            message = "False"
        else:
            message = "Error"

        result = g.conn.execute("SELECT fuid FROM Is_Friend WHERE uid ='{0}' ".format(uid)).fetchall()
        friendlist = []
        for f in result:
            person = g.conn.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE uid ='{0}' ".
                format(f[0])).fetchone()
            friendlist.append(person)
        recommand = user_resource.getRecommandFriend(uid)
        return render_template('addfriend.html', message=message, friendlist=friendlist, recommand=recommand)


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

    """

    # DEBUG: this is debugging code to see what request looks like
    # print(request.args)

    #
    # example of a database query
    #
    # cursor = g.conn.execute("SELECT name FROM test")
    # names = []
    # for result in cursor:
    #   names.append(result['name'])  # can also be accessed using result[0]
    # cursor.close()

    cursor = g.conn.execute("SELECT * FROM users")
    names = []
    for result in cursor:
        names.append(result)  # can also be accessed using result[0]
    cursor.close()

    print(names)

    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    if flask_login.current_user.is_authenticated == False:
        return render_template("hello.html")
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        return render_template("hello.html", name=user_resource.getUsersName(uid), message="Here's your profile")


#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

def getUserList():
    users = g.conn.execute("SELECT email from Users").fetchall()
    return users


def getUserIdFromEmail(email):
    result = g.conn.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email)).fetchone()
    print("Getting uid:", result, result[0])
    return result[0]


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    cursor = g.conn
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    if request.form['password'] == pwd:
        user.id = email
        return user
    return None


@app.route('/profile')
@flask_login.login_required
def protected():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    print("uid is:", uid)
    return render_template('hello.html', name=user_resource.getUsersName(uid), message="Here's your profile")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return user_resource.get_login_page()
    else:
        # The request method is POST (page is recieving data)
        email = request.form['email']
        password = request.form['password']
        return user_resource.post_login_page(email, password)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress=True)


@app.route("/register", methods=['POST'])
def register_user():
    form_data = request.form
    return user_resource.register_account(form_data)


@app.route('/album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        return album_resource.post_create_album(uid, form_data=request.form)

    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('album.html', album=user_resource.getUsersAlbums(uid))


@app.route("/onealbum", methods=['GET', 'POST'])
@flask_login.login_required
def onealbum():
    # if flask_login.current_user.is_authenticated == False:
    #     uid = getUserIdFromEmail("anonymous@bu.edu")
    # else:
    uid = getUserIdFromEmail(flask_login.current_user.id)

    if request.method == 'POST':
        return album_resource.post_onealbum(uid, request)
    else:
        return album_resource.get_onealbum(uid, args_data=request.args)


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'GET':
        return photo_resource.get_upload_photo(aid=request.args.get('aid'))
    else:
        return photo_resource.post_upload_photo(uid, request)

@app.route("/browse", methods=['GET','POST'])
#@flask_login.login_required
def browse():
    if flask_login.current_user.is_authenticated == False:
        uid = getUserIdFromEmail("anonymous@columbia.edu")
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)

    if request.method=='GET':
        return general_resource.get_browse(uid)
    else:
        cursor = conn.cursor()
        aid = request.form.get('aid')
        owneruid = getAlbumOwner(aid)
        comment = request.form.get('comment')
        date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
        uname = getUsersName(uid)
        pid=request.form.get('pid')
        cursor.execute(
            '''INSERT INTO  Comments_Leaves_Has (comment,date, pid, aid,uid,uname) VALUES (%s, %s,%s,%s, %s,%s )''',
            (comment, date, pid, aid, uid, uname))
        newcontribution = getUserContribution(uid) + 1
        cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid,newcontribution))
        conn.commit()
        photos = getAllPhotos()
        return render_template('browse.html', uid=uid, users=photos, base64=base64)


if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python3 server.py

        Show the help text using:

            python3 server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
