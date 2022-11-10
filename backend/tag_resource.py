import flask_login
from flask import Flask, request, render_template, g, redirect, Response, url_for

from backend import album_resource,user_resource, photo_resource, general_resource
from datetime import datetime

def getAllTags():
    result = g.conn.execute("SELECT tag_name FROM Tags ORDER BY tag_name").fetchall()
    return result  # NOTE list of tuples, [(tag_name,), ...]

def getTopTags():
    result = g.conn.execute("SELECT Tags.tag_name FROM Tags, Associates WHERE Tags.tag_name=Associates.tag_name GROUP BY Tags.tag_name ORDER BY COUNT(*) DESC").fetchall()
    return result  # NOTE list of tuples, [(tag_name,), ...]

def getPhotoByTag(tag_name):
    result = g.conn.execute("SELECT pid FROM Associates WHERE tag_name = '{0}'".format(tag_name)).fetchall()
    return result

def get_onetag(uid,request):
    tag_name = request.args.get('description')
    photolist = []
    photo_id = getPhotoByTag(tag_name)
    for photo in photo_id:
        pid = photo[0]
        photo_data = photo_resource.getPhoto(pid)
        comments = photo_resource.getPhotoComment(pid)  # (text, date, pid, uname)tuple
        photo_comment = []
        for comment in comments:
            photo_comment.append({'text': comment[0], 'date': comment[1], 'user_name': comment[3]})
        tags = photo_resource.getPhotoTag(pid)  # (tag_name,pid) tuple
        numlikes = photo_resource.getNumLikes(pid)
        (owner_uid,aid) = photo_resource.getPhotoOwner_Album(pid)
        owner_name = user_resource.getUsersName(owner_uid)
        photolist.append(
            {'pid': pid, 'caption': photo_data[1], 'img_data': photo_data[2], 'tags': tags, 'numlikes': numlikes,
             'comments': photo_comment, 'owner_id':owner_uid,'owner_name':owner_name, 'aid':aid})

    return render_template('/onetag.html', description=tag_name, uid=uid, photos=photolist)

def post_onetag(uid):
    cursor = conn.cursor()
    comment = request.form.get('comment')
    date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
    uname = getUsersName(uid)
    pid = request.form.get('pid')
    aid = getAlbumId(pid)
    cursor.execute(
        '''INSERT INTO  Comments_Leaves_Has (comment,date, pid, aid,uid,uname) VALUES (%s, %s,%s,%s, %s,%s )''',
        (comment, date, pid, aid, uid, uname))
    newcontribution = getUserContribution(uid) + 1
    cursor.execute("UPDATE Users SET contribution='{1}'  WHERE uid = '{0}'".format(uid, newcontribution))
    conn.commit()
    description = request.args.get('description')
    photolist = []
    photos = getPhotoByTag(description)
    for photo in photos:
        pid = photo[1]
        if pid == -1:
            continue
        owneruid = photo[2]
        ownername = getUsersName(owneruid)
        photodata = getPhoto(pid)
        numlikes = getNumLikes(pid)
        comment = getPhotoComment(pid)
        tags = getPhotoTag(pid)
        photolist.append([photodata, numlikes, comment, tags, ownername, aid])
    return render_template('/onetag.html', description=description, uid=uid, photos=photolist)