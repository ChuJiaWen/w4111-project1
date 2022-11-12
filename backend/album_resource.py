from flask import Flask, request, render_template, g, redirect, Response, url_for
from backend import user_resource, photo_resource, tag_resource, general_resource
from datetime import datetime


def getAlbumName(aid):
    result = g.conn.execute("SELECT name FROM Albums WHERE aid ='{0}'".format(aid)).fetchone()
    return result[0]

def getAlbumOwner(aid):
    result = g.conn.execute("SELECT uid FROM Albums WHERE aid ='{0}'".format(aid)).fetchone()
    return result[0]

def getAlbumPhotos(aid):
    # print(g.conn.execute("SELECT pid FROM Contains WHERE aid ='{0}'".format(aid)).fetchall())
    result = g.conn.execute("SELECT pid FROM Contains WHERE aid ='{0}'".format(aid)).fetchall()
    return result

def post_create_album(uid, form_data):
    distinction = request.form.get('distinction')
    if distinction == '0':
        album_name = request.form.get('name')
        g.conn.execute('''INSERT INTO Albums (uid, name) VALUES (%s, %s )''', (uid, album_name))
        return render_template('album.html', album=user_resource.getUsersAlbums(uid), message='Album created!')
    elif distinction == '1':
        aid = request.form.get('aid')
        name = getAlbumName(aid)
        photos = getAlbumPhotos(aid)
        # comments = getAlbumComments(aid)
        # for comment in comments:
        #     cuid = comment[4]
        # for photo in photos:
        #     pid = photo[1]
        #     cursor.execute("UPDATE Associates SET pid='-1'  WHERE pid = '{0}'".format(pid))

        g.conn.execute("DELETE FROM Albums WHERE aid='{0}'".format(aid))
        string = "Album " + name + " deleted."
        return render_template('album.html', album=user_resource.getUsersAlbums(uid), message=string)
    else:
        aid = request.form.get('aid')
        newname = request.form.get('newname')
        oldname = getAlbumName(aid)
        g.conn.execute("UPDATE Albums SET name='{1}'  WHERE aid = '{0}'".format(aid, newname))
        string = "Album " + oldname + " renamed to " + newname + "."
        return render_template('album.html', album=user_resource.getUsersAlbums(uid), message=string)

def get_onealbum(uid, aid):
    owneruid = getAlbumOwner(aid)
    ownername= user_resource.getUsersName(owneruid)
    photo_id = getAlbumPhotos(aid)
    photolist = []
    for pid in photo_id:
        pid=pid[0]
        photo = photo_resource.getPhoto(pid)
        numlikes = photo_resource.getNumLikes(pid)
        tags = photo_resource.getPhotoTag(pid)
        comments = photo_resource.getPhotoComment(pid) #(text, date, pid, uname)tuple
        photo_comment = []
        for comment in comments:
            photo_comment.append({'text': comment[0], 'date':comment[1],'user_name':comment[3]})
        photolist.append([photo, numlikes, photo_comment, tags])
    return render_template('onealbum.html', uid=uid, owneruid=owneruid, ownername=ownername,name=getAlbumName(aid), aid=aid, photos=photolist)

def post_onealbum(uid, request):
    aid = request.args.get('aid')
    pid = request.form.get('pid')
    distinction = request.form.get('distinction')

    if distinction == '0':
        comment = request.form.get('comment')
        date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
        pid = request.form.get('pid')
        g.conn.execute(
            '''INSERT INTO  Has_Comments (text, date, pid) VALUES (%s, %s, %s)''',
            (comment, date, pid))
        cid = g.conn.execute("SELECT cid FROM Has_Comments ORDER BY cid DESC LIMIT 1;").fetchone()[0]
        g.conn.execute('''INSERT INTO Commented (cid,pid, uid, date) VALUES (%s, %s, %s, %s )''',
                       (cid, pid, uid, date))
    else:
        g.conn.execute("DELETE FROM Photos WHERE pid='{0}'".format(pid))
    return get_onealbum(uid, aid)

def getAlbumId(pid):
    res = g.conn.execute("SELECT aid FROM Contains WHERE pid ='{0}'".format(pid)).fetchone()
    return res[0]