from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
from sqlalchemy import desc
import spotipy
import spotipy.util as util
import sys

spotify = spotipy.Spotify()




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:letsseshify@10.38.45.98:5432/seshify'
app.debug = True
db = SQLAlchemy(app)

class Song():
    spotify_song_id = ""
    song_name = ""
    artist = ""
    album = ""

    def __init__(self, song_dictionary):
        self.spotify_song_id = song_dictionary['uri']
        self.song_name = song_dictionary['name']
        self.artist = song_dictionary['artists'][0]['name']
        self.album = song_dictionary['album']['name']


class RequestedSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_song_id = db.Column(db.String(120))
    title = db.Column(db.String(120))
    artist = db.Column(db.String(120))
    album = db.Column(db.String(120))
    upvotes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    party_id = db.Column(db.Integer)

    def __init__(self, song_id):
        song_dictionary = spotify.track(song_id)
        print song_dictionary
        self.spotify_song_id = song_id
        self.title = song_dictionary['name']
        self.artist = song_dictionary['artists'][0]['name']
        self.album = song_dictionary['album']['name']
        self.upvotes = 1
        self.downvotes = 0

    def __repr__(self):
        return '<QueuedSong %r>' % self.song_id

class Party(db.Model):
    party_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    host_id = db.Column(db.Integer)

    def __init__(self, name, host_id):
        self.name = name
        self.host_id = host_id


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    spotify_username = db.Column(db.String(120))

    def __init__(self, spotify_username):
        self.spotify_username = spotify_username




@app.route('/', methods=['GET', 'POST'])
def display_requested_songs():
    if request.method == 'POST':
        #if the upvote button was pressed
        if 'upvote' in request.form :
            #get the song that was clicked
            song = RequestedSong.query.filter_by(id=request.form['upvote']).first()
            #increment number of upvotes
            song.upvotes = song.upvotes + 1
        #if the downvote button was pressed
        elif 'downvote' in request.form:
            #get the song that was clicked
            song = RequestedSong.query.filter_by(id=request.form['downvote']).first()
            #decrement the number of downvotes
            song.downvotes = song.downvotes + 1
        #if you want to queue the song
        elif 'queue' in request.form:
            #get the song that was clicked
            #song = RequestedSong.query.filter_by(id=request.form['queue']).first()
            #decrement the number of downvotes
            print('====================================')
            print request.form['queue']
            add_to_playlist('seshify', '6pABjrw5lb1NvfKoT7F3kD', [request.form['queue']])

        #save the database
        db.session.commit()
    #gets all the songs ordered by the id
    songs = RequestedSong.query.filter_by().order_by(desc("upvotes"))

    return render_template('create.html', songs=songs)

token = ""


def add_to_playlist(username, playlist_id, track_ids):
    scope = 'playlist-modify-public'
    print '============================'
    print username
    global token
    if token == "":
        token = util.prompt_for_user_token(username, scope, client_id='e86d0b147dbf45dfb68a9a20bd26b9af',
                                           client_secret='915c3a30c3d046b690703b2acde2183e',
                                           redirect_uri='http://localhost/')

    print '**************************************************'
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
        print results
    else:
        print "Can't get token for", username

@app.route('/addsongs', methods=['GET', 'POST'])
def create_song_request():
    print "====================="
    songs = []
    if request.method == 'POST':
        #if you click the request button
        if 'request_song' in request.form:
            print 'add song to request database'
            uri = request.form['request_song']
            request_song(uri)

        #if you click the search button
        elif 'search' in request.form:
            if request.form['searchbox'] != "":
                songs = search_song(request.form['searchbox'])
        db.session.commit()
    #gets all the songs ordered by the id
    return render_template('startparty.html', songs=songs)

#returns a list of song objects that correspond to the search string
def search_song(search_string):
    #search spotify for string
    results = spotify.search(q=search_string, type='track')
    items = results['tracks']['items']
    songs=[]
    #for each song
    if len(items) > 0:
        for x in range(0, 10):
            song = Song(items[x])
            songs.append(song)
    return songs



#this adds the song to the requested list
def request_song(song_id):
    print("test");


def request_song(song_id):
    song = RequestedSong(song_id)
    db.session.add(song)
    db.session.commit()


if __name__ == '__main__':
    app.run()
