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

def getRecommandFriend(uid):
    result = g.conn.execute("SELECT fuid FROM Is_Friend WHERE uid ='{0}' ".format(uid)).fetchall()
    friendlist = []
    for f in result:
        person = g.conn.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE uid ='{0}' ".
                       format(f[0])).fetchall()[0]
        friendlist.append(person)
    count = {}
    for f in result:
        fuid = f[0]
        ff = getUserFriendId(fuid)
        for stranger in ff:
            if stranger[0] == uid:
                continue
            if stranger not in result and stranger[0] not in count:
                count[stranger[0]] = 1
            elif stranger not in result:
                count[stranger[0]] = count[stranger[0]] + 1
    recommand = []
    count = sorted(count.items(), key=lambda item: item[1], reverse=True)
    for fuid in count:
        if fuid[1] != 0:
            user = g.conn.execute(
                "SELECT first_name, last_name, email, DOB, hometown, gender, uid FROM Users WHERE uid ='{0}' ".
                    format(fuid[0])).fetchone()
            recommand.append([user, fuid[1]])
    return recommand

def getUserIdFromEmail(email):
    userId = g.conn.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email)).fetchall()
    return userId[0][0]

def getUserFriend(uid):
    friendlist = []
    # cursor = conn.cursor()
    result = g.conn.execute("SELECT fuid FROM Is_Friend WHERE uid ='{0}' ".format(uid)).fetchall()
    for f in result:
        info = g.conn.execute("SELECT first_name, last_name, email, DOB, hometown, gender FROM Users WHERE uid ='{0}' ".
                              format(f[0])).fetchall()[0]
        friendlist.append(info)
    return friendlist

def getUserFriendId(uid):
    return g.conn.execute("SELECT fuid FROM Is_Friend WHERE uid = '{0}'".format(uid)).fetchall()

def getAllPhotos():
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT uid FROM Photos")
    uidlist = cursor.fetchall()
    users=[]
    for uid in uidlist:
        users.append([uid[0],getUsersName(uid[0])])
    for j in range(0,len(users)):
        #[(uid,firstname),[(aid,name)]]
        albums=getUsersAlbums(users[j][0])
        for z in range(0,len(albums)):
            aid=albums[z][0]
            aname =albums[z][1]
            users[j].append([])
            users[j][2].append([aid,aname,[],[]])
            comments = getAlbumComments(aid)
            for i in range(0,len(comments)):
                users[j][2][z][3].append(comments[i])
            photos=getAlbumPhotos(aid)
            for i in range(0,len(photos)):
                pid=photos[i][1]
                if pid == -1:
                    continue
                numlikes = getNumLikes(photos[i][1])
                tags = getPhotoTag(pid)
                users[j][2][z][2].append([photos[i], numlikes,tags])
    return users