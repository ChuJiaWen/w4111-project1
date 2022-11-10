from flask import request, render_template, g
from backend import user_resource, photo_resource, album_resource, tag_resource
from datetime import datetime

def get_browse(uid):
    photos = user_resource.getAllPhotos(uid)
    taglist = tag_resource.getTopTags()
    return render_template('browse.html', uid=uid, user_photos=photos, taglist=taglist)

def post_browse(uid, request):
    aid = request.form.get('aid')
    owneruid = album_resource.getAlbumOwner(aid)
    comment = request.form.get('comment')
    date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
    uname = user_resource.getUsersName(uid)
    pid = request.form.get('pid')
    g.conn.execute(
        '''INSERT INTO  Has_Comments (text, date, pid) VALUES (%s, %s, %s)''',
        (comment, date, pid))
    cid = g.conn.execute("SELECT cid FROM Has_Comments ORDER BY cid DESC LIMIT 1;").fetchone()[0]
    g.conn.execute('''INSERT INTO Commented (cid,pid, uid, date) VALUES (%s, %s, %s, %s )''',
                   (cid,pid, uid, date))
    photos = user_resource.getAllPhotos(uid)
    taglist = tag_resource.getTopTags()
    return render_template('browse.html', uid=uid, user_photos=photos, taglist=taglist)