import flask_login
from flask import Flask, request, render_template, g, redirect, Response
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

def getUserIdFromEmail(email):
    result = g.conn.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email)).fetchone()
    print("Getting uid:",result, result[0])
    return result[0]

def getUsersName(uid):
    result = g.conn.execute("SELECT first_name FROM Users WHERE uid = '{0}'".format(uid)).fetchone()
    return result[0]
