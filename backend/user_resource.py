import json

import flask_login
from flask import Flask, request, render_template, g, redirect, Response, url_for
from backend import photo_resource, album_resource, tag_resource


class User(flask_login.UserMixin):
    pass

def get_login_page():
    return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
           <a href='/'>Home</a> <br>
           <a href='/register'> Register </a>
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

def is_private(uid):
    return g.conn.execute("SELECT is_private FROM Users WHERE uid = '{0}'".format(uid)).fetchone()[0]

def is_friend(uid,fuid):
    result = g.conn.execute("SELECT COUNT(*)  FROM Is_Friend WHERE uid = '{0}' AND fuid = '{1}'".format(uid,fuid)).fetchone()
    if len(result) != 0:
        return True
    else:
        return False

def getAllPhotos(uid):
    """uid = current logged-in user; user_id = accounts in database"""
    uidlist = g.conn.execute("SELECT DISTINCT uid FROM Users").fetchall()
    users=[]
    user_photos=[]
    for user in uidlist:
        #get photos of an account if it satisfies one of the condition
        owner_id=user[0]
        if not is_private(owner_id):#if account is public
            users.append([owner_id,getUsersName(owner_id)])
        elif is_private(owner_id) and is_friend(uid,owner_id): #if account is private and user is account's friend
            users.append([owner_id, getUsersName(owner_id)])
    # print("This is users inside user_resource/getAllPhotos:", users)
    """
    user1 = '{  'owner_id' : owner_id,
                "owner_name": owner_name,
                "albums" : { "aid":aid, "album_name": aname, "photos": {"pid": pid, "caption":caption, "img_data":img_data, 
                                                                        "tags": tags(list of tags), "numlikes": numlikes, 
                                                                        "comments": {"text":comment_text, "date":datae
                                                                         "user_name":comment_uname}}}
    }'
    """
    for (owner_id, owner_name) in users:
        #[(uid,firstname),[(aid,name)]]
        albums=getUsersAlbums(owner_id) #(aid, name) tuple
        album_data = []
        for album in albums:
            aid = album[0]
            aname =album[1]
            photo_id=album_resource.getAlbumPhotos(aid)
            album_photos=[]
            for photo in photo_id:
                pid = photo[0]
                photo_data = photo_resource.getPhoto(pid) #(pid, caption, img_data) tuple
                comments = photo_resource.getPhotoComment(pid) #(text, date, pid, uname)tuple
                photo_comment = []
                for comment in comments:
                    photo_comment.append({'text': comment[0], 'date':comment[1],'user_name':comment[3]})
                tags = photo_resource.getPhotoTag(pid) #(tag_name,pid) tuple
                numlikes = photo_resource.getNumLikes(pid)
                album_photos.append({'pid':pid, 'caption':photo_data[1],'img_data':photo_data[2],'tags':tags, 'numlikes':numlikes,'comments':photo_comment})
            if len(album_photos)>0:
                album_data.append({'aid':aid, 'album_name':aname,'photos':album_photos})
        if len(album_data)>0:
            user_photos.append({'owner_id':owner_id, 'owner_name':owner_name, 'albums':album_data})
    return user_photos

