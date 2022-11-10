from flask import request, render_template, g
from backend import user_resource, photo_resource, album_resource, tag_resource
from datetime import datetime


def getPoplarPhotos():
    result = []
    cursor = g.conn.execute("SELECT L.pid FROM Likes L GROUP BY L.pid ORDER BY COUNT(*) DESC LIMIT 5")
    # for row in cursor:
    #     photo_ownerid = photo_resource.getPhotoOwner_Album(row[0])[0]
    #     if not user_resource.is_private(photo_ownerid) or user_resource.is_friend(uid,photo_ownerid):
    #         result.append(row)
    # return result
    return cursor.fetchall()


def getPoplarPhotoInfo():
    photolist = []
    photo_id = getPoplarPhotos()
    for photo in photo_id:
        pid = photo[0]
        photo_data = photo_resource.getPhoto(pid)
        comments = photo_resource.getPhotoComment(pid)  # (text, date, pid, uname)tuple
        photo_comment = []
        for comment in comments:
            photo_comment.append({'text': comment[0], 'date': comment[1], 'user_name': comment[3]})
        tags = photo_resource.getPhotoTag(pid)  # (tag_name,pid) tuple
        numlikes = photo_resource.getNumLikes(pid)
        (owner_uid, aid) = photo_resource.getPhotoOwner_Album(pid)
        owner_name = user_resource.getUsersName(owner_uid)
        photolist.append(
            {'pid': pid, 'caption': photo_data[1], 'img_data': photo_data[2], 'tags': tags, 'numlikes': numlikes,
             'comments': photo_comment, 'owner_id': owner_uid, 'owner_name': owner_name, 'aid': aid})
    return photolist


def get_browse(uid):
    photos = user_resource.getAllPhotos(uid)
    taglist = tag_resource.getTopTags()
    return render_template('browse.html', uid=uid, user_photos=photos, taglist=taglist)


def post_browse(uid, request):
    comment = request.form.get('comment')
    date = datetime.today().strftime('%Y-%m-%d,%H:%M:%S')
    pid = request.form.get('pid')
    g.conn.execute(
        '''INSERT INTO  Has_Comments (text, date, pid) VALUES (%s, %s, %s)''',
        (comment, date, pid))
    cid = g.conn.execute("SELECT cid FROM Has_Comments ORDER BY cid DESC LIMIT 1;").fetchone()[0]
    g.conn.execute('''INSERT INTO Commented (cid,pid, uid, date) VALUES (%s, %s, %s, %s )''',
                   (cid, pid, uid, date))
    return get_browse(uid)
