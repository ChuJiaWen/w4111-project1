from flask import request, render_template, g
from backend import user_resource, photo_resource, album_resource, tag_resource

def get_browse(uid):
    photos = user_resource.getAllPhotos(uid)
    taglist = tag_resource.getAllTags()
    return render_template('browse.html', uid=uid, users=photos, taglist=taglist)