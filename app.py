import flask
import musictext
import os
import pymongo
import bson
import hashlib
import datetime
import grako
import json

app = flask.Flask(__name__)

mongoclient = pymongo.MongoClient()
musictext_db = mongoclient['musictext']
wav_coll = musictext_db['wav']

@app.route('/')
def route_index():
    print(flask.url_for('static', filename='index.html'))
    return flask.redirect(flask.url_for('static', filename='index.html'))

@app.route('/wav', methods=['POST'])
def route_wav_post():
    mt = flask.request.form.get('musictext')
    
    hash = hashlib.sha1()
    hash.update(mt.encode())
    song_id = hash.hexdigest()
    
    try:
        wav = musictext.musictext_to_wav(mt)
    except grako.exceptions.FailedParse as e:
        return json.dumps({'success': False, 'message': str(e)})
    
    wav_coll.update_one({'_id': song_id}, {'$set': {
        'musictext': mt,
        'wav': bson.binary.Binary(wav),
        'date': datetime.datetime.now()
    }}, upsert=True)
    
    return json.dumps({'success': True, 'song_id': song_id})

@app.route('/wav')
def route_wav():
    song_id = flask.request.args.get('song_id')
    if song_id is None:
        return 'Query parameter song_id is missing', 400
    print(song_id)
    doc = wav_coll.find_one(song_id)
    if doc is not None:
        wav = doc['wav']
        return flask.Response(wav, mimetype='audio/wav')
    else:
        return 'No song with that song_id', 404