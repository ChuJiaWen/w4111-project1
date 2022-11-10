import flask_login
from flask import Flask, request, render_template, g, redirect, Response, url_for

from backend import album_resource,user_resource
from datetime import datetime

def getAllTags():
    result = g.conn.execute("SELECT tag_name FROM Tags ORDER BY tag_name").fetchall()
    return result  # NOTE list of tuples, [(tag_name,), ...]

def getTopTags():
    result = g.conn.execute("SELECT Tags.tag_name FROM Tags, Associates WHERE Tags.tag_name=Associates.tag_name GROUP BY Tags.tag_name ORDER BY COUNT(*) DESC").fetchall()
    return result  # NOTE list of tuples, [(tag_name,), ...]

# def getTopMyTags(uid):
#     result = g.conn.execute("SELECT description, count(pid) as count FROM Tags_Associates WHERE uid='{0}' GROUP BY description ORDER BY count DESC LIMIT 5".format(uid)).fetchall()
#     return result

# def getMyTags(uid):
#     result = g.conn.execute("SELECT description, pid FROM Associates WHERE  uid = '{0}'".format(uid)).fetchall()
#     return result  # NOTE list of tuples, [(description, pid), ...]

# def getTagsPhotosAll(description):
#     result = g.conn.execute("SELECT description, pid FROM Tags_Associates WHERE description = '{0}'".format(description)).fetchall()
#     return result  # NOTE list of tuples, [(description, pid), ...]

# def getTagsPhotosMy(description,uid):
#     result = g.conn.execute("SELECT description, pid FROM Tags_Associates WHERE description = '{0}' AND uid = '{1}'".format(description,uid)).fetchall()
#     return result  # NOTE list of tuples, [(description, pid), ...]