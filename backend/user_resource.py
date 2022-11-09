import flask_login
from flask import Flask, request, render_template, g, redirect, Response, url_for


class User(flask_login.UserMixin):
    pass

def get_login_page():
    return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
           <a href='/'>Home</a>
               '''

def post_login_page(email,password):
    result = g.conn.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)).fetchall()
    # check if email is registered
    if len(result) > 0:
        # data = cursor.fetchall()
        # pwd = str(data[0][0] )
        pwd = str(result[0]['password'])
        if password == pwd:
            print("Password matches!")
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user

            return redirect(url_for('protected'))  # protected is a function defined in this file

    # information did not match
    print("Email not found or password not correct")
    return "<a href='/login'>Try again</a>\
                    </br><a href='/register'>or make an account</a>"

def isEmailUnique(email):
    #use this to check if a email has already been registered
    result = g.conn.execute("SELECT COUNT(email)  FROM Users WHERE email = '{0}'".format(email)).fetchall()

    if result[0][0] != 0:
        #this means there are greater than zero entries with that email
        print("Email:",email,"already in use")
        return False
    else:
        # print("Email:",email,"not in use")
        return True

def register_account(form_data):
    try:
        email=form_data.get('email')
        password=form_data.get('password')
        first_name = form_data.get('first_name')
        last_name = form_data.get('last_name')
        hometown = form_data.get('hometown')
        gender = form_data.get('gender')
        DOB = form_data.get('DOB')
        is_private = form_data.get('is_private')
    except:
        print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
        return redirect(url_for('register'))
    cursor = g.conn
    test =  isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, password,first_name,last_name,hometown,gender, DOB,is_private) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}','{6}',{7})".format(email, password,first_name,last_name,hometown,gender, DOB,is_private)))
        # conn.commit()
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=first_name, message='Account Created!')
    else:
        return render_template('register.html', supress=False)

def getUserIdFromEmail(email):
    result = g.conn.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email)).fetchone()
    print("Getting uid:",result, result[0])
    return result[0]

def getUsersName(uid):
    result = g.conn.execute("SELECT first_name FROM Users WHERE uid = '{0}'".format(uid)).fetchone()
    return result[0]

def getUsersAlbums(uid):
    result = g.conn.execute("SELECT aid, name FROM Albums WHERE uid = '{0}'".format(uid)).fetchall()
    return result #NOTE list of tuples, [(imgdata, pid), ...]
