import string

from flask import render_template, g, redirect
import mimetypes, urllib

from backend import album_resource, tag_resource
from datetime import datetime


def is_url_image(url):
    mimetype, encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))


def getPhoto(pid):
    result = g.conn.execute("SELECT pid, caption, img_data FROM Photos WHERE pid = '{0}'".format(pid)).fetchone()
    # print("Inside photo_resource/getPhoto(pid), this is info retrived:",result)
    return result


def getPhotoOwner_Album(pid):
    result = g.conn.execute(
        "SELECT Albums.uid, Albums.aid FROM Albums, Contains WHERE Contains.pid ='{0}' AND Contains.aid=Albums.aid".format(
            pid)).fetchone()
    return result


def getPhotoComment(pid):
    result = g.conn.execute("SELECT text, Has_Comments.date, Has_Comments.pid, Users.first_name FROM Has_Comments,Commented, Users \
    WHERE Has_Comments.pid ='{0}' AND Commented.pid = '{0}' AND Has_Comments.cid=Commented.cid AND Users.uid=Commented.uid".format(
        pid)).fetchall()
    return result


def getPhotoTag(pid):
    result = g.conn.execute("SELECT tag_name FROM Associates WHERE pid = '{0}'".format(pid)).fetchall()
    # print("This is tags retrived from photo_resource/getPhotoTag:", result)
    return result


def getNumLikes(pid):
    result = g.conn.execute("SELECT COUNT(*) FROM Likes WHERE pid='{0}'".format(pid)).fetchone()
    return result[0]


def get_upload_photo(aid):
    albumname = album_resource.getAlbumName(aid)
    tags = tag_resource.getAllTags()
    return render_template('upload.html', aid=aid, albumname=albumname, tags=tags)


def post_upload_photo(uid, request):
    aid = request.form.get('aid')
    img_data = request.form['photo_url']
    aname = album_resource.getAlbumName(aid)
    if not is_url_image(img_data):  # check if the url is really a photo
        tags = tag_resource.getAllTags()
        return render_template('upload.html', aid=aid, albumname=aname,tags=tags, message="The URL you entered does not return an image. Please try another one.")
    else:
        caption = request.form.get('caption')
        choosedtags = request.form.getlist('choosetag')
        date = datetime.today().strftime('%Y-%m-%d')
        newtag = request.form.get('newtag').lower()
        if newtag:
            if newtag[len(newtag) - 1] == ";":
                newtag = newtag[:-1]
        newtags = newtag.split(";")
        # print("after split, New tags look like these:", newtag)
        # newtags = list(dict.fromkeys(newtags))
        g.conn.execute('''INSERT INTO Photos (img_data,caption) VALUES (%s, %s )''',
                       (img_data, caption))
        pid = g.conn.execute("SELECT pid FROM Photos ORDER BY pid DESC LIMIT 1;").fetchone()[0]
        # print("This is the pid retrived from select in photo_resource/post_upload_photo", pid)
        g.conn.execute('''INSERT INTO Contains (pid,aid, date) VALUES (%s, %s, %s )''',
                       (pid, aid, date))

        if newtags != [''] and newtags != [""] and newtags != None and newtags != []:
            for tag in newtags:
                tag =tag.translate({ord(c):None for c in string.whitespace})#remove whitespaces
                choosedtags.append(tag)
                g.conn.execute('''INSERT INTO Tags (tag_name) VALUES (%s)''', (tag))
        choosedtags = list(dict.fromkeys(choosedtags))
        if choosedtags != [] and choosedtags != [""]:
            for tag in choosedtags:
                if tag == '' or tag == ' ' or tag is None:
                    continue
                g.conn.execute('''INSERT INTO Associates (tag_name,pid) VALUES (%s, %s)''', (tag, pid))
        photo_id = album_resource.getAlbumPhotos(aid)
        photolist = []
        for pid in photo_id:
            pid = pid[0]
            photo = getPhoto(pid)
            tags = getPhotoTag(pid)
            numlikes = getNumLikes(pid)
            photolist.append([photo, numlikes, tags])
        return render_template('onealbum.html', aid=aid, albumname=aname, message='Photo uploaded!',
                               photos=photolist)


def findOwnerByPid(pid):
    result = g.conn.execute(
        "SELECT a.uid FROM Contains c, Albums a WHERE a.aid=c.aid AND c.pid = '{0}'".format(pid)).fetchone()
    return result[0]
