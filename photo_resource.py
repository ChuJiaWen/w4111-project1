import flask_login
from flask import Flask, request, render_template, g, redirect, Response, url_for

import album_resource,user_resource,tag_resource
from datetime import datetime

def getPhoto(pid):
    result = g.conn.execute("SELECT  pid, caption, img_data FROM Photos WHERE pid = '{0}'".format(pid)).fetchone()
    print("Inside photo_resource/getPhoto(pid), this is info retrived:",result)
    return result

def getPhotoOwner(pid):
    result = g.conn.execute("SELECT uid FROM Photos WHERE pid ='{0}'".format(pid)).fetchone()
    return result[0]

def getPhotoComment(pid):
    result = g.conn.execute("SELECT text, Has_Comments.date, Has_Comments.pid,uid FROM Has_Comments,Commented \
    WHERE Has_Comments.pid ='{0}' AND Commented.pid = '{0}' AND Has_Comments.cid=Commented.cid".format(pid)).fetchall()
    return result

def getPhotoTag(pid):
    result = g.conn.execute("SELECT tag_name,pid FROM Associates WHERE pid = '{0}'".format(pid)).fetchall()
    return result

def getNumLikes(pid):
    result = g.conn.execute("SELECT COUNT(*) FROM Likes WHERE pid='{0}'".format(pid)).fetchone()
    return result[0]  # NOTE list of tuples, [(description, pid), ...]

def get_upload_photo(aid):
    albumname = album_resource.getAlbumName(aid)
    tags = tag_resource.getAllTags()
    return render_template('upload.html', aid=aid, albumname=albumname, tags=tags)

def post_upload_photo(uid, request):
    aid = request.form.get('aid')
    img_data = request.form['photo_url']
    caption = request.form.get('caption')
    newtag = request.form.get('newtag')
    newtag = newtag.lower()
    if newtag:
        if newtag[len(newtag) - 1] == ";":
            newtag = newtag[:-1]
    newtags = newtag.split(";")
    print("after split, New tags look like these:", newtag)
    # newtags = list(dict.fromkeys(newtags))
    choosedtags = request.form.getlist('choosetag')
    date = datetime.today().strftime('%Y-%m-%d')
    g.conn.execute('''INSERT INTO Photos (img_data,caption) VALUES (%s, %s )''',
                   (img_data, caption))
    pid = g.conn.execute("SELECT pid FROM Photos ORDER BY pid DESC LIMIT 1;").fetchone()[0]
    print("This is the pid retrived from select in photo_resource/post_upload_photo",pid)
    g.conn.execute('''INSERT INTO Contains (pid,aid, date) VALUES (%s, %s, %s )''',
                   (pid, aid, date))

    if newtags != [''] and newtags != [""] and newtags != None and newtags != []:
        for tag in newtags:
            choosedtags.append(tag)
            g.conn.execute('''INSERT INTO Tags (tag_name) VALUES (%s)''',(tag))
    choosedtags = list(dict.fromkeys(choosedtags))
    if choosedtags != [] and choosedtags != [""]:
        for tag in choosedtags:
            if tag == '' or tag == ' ' or tag is None:
                continue
            g.conn.execute('''INSERT INTO Associates (tag_name,pid) VALUES (%s, %s)''',(tag, pid))
    photo_id = album_resource.getAlbumPhotos(aid)
    photolist = []
    for pid in photo_id:
        pid = pid[0]
        photo = getPhoto(pid)
        tags = getPhotoTag(pid)
        numlikes = getNumLikes(pid)
        photolist.append([photo, numlikes, tags])
    return render_template('onealbum.html', aid=aid, name=album_resource.getAlbumName(aid), message='Photo uploaded!',
                           photos=photolist)
