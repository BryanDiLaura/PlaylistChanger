#Bryan DiLaura

from flask import Flask, request, render_template, redirect, url_for
import spotipy
from webbrowser import open_new_tab
import random
import datetime

app = Flask(__name__)

from keys import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

#don't change these!
SPOTIPY_REDIRECT_URI = 'http://localhost:5000'
SCOPE = 'user-library-read user-read-recently-played playlist-modify-public user-top-read'
CACHE = '.spotipyoauthcache'

sp_oauth = spotipy.oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

#global spotify object forward instatiation (defined in index())
sp = None


@app.route('/',methods=["POST","GET"])
def index():
    #Authorization workflow borrowed heavily from github user perelin
    #original found here: https://github.com/perelin/spotipy_oauth_demo
    global sp
    access_token = ""

    token_info = sp_oauth.get_cached_token()

    #is there a cached token?
    if token_info:
        print ("Found cached token!")
        access_token = token_info['access_token']
    
    #try to get a new access token
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print ("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    #if we have everything we need, so create the spotify object
    if access_token:
        print ("Access token available! Creating spotify object")
        sp = spotipy.Spotify(access_token)
        return redirect(url_for("top_tracks"))

    #need to prompt user to log in
    else:
        auth_url = getSPOauthURI()
        return render_template("index.html", auth_url=auth_url)


def getSPOauthURI():
    #helper for creating a oauth url
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


@app.route("/top_tracks")
def top_tracks():
    global sp
    user = sp.current_user()
    top = sp.current_user_top_tracks(limit=10)
    createNewlyAddedPlaylist(maxSongsPerArtist=3)
    return render_template("topSongs.html", songs=top['items'], user=user['id'])


def filterPlaylists(songs, artistDict, maxSongsPerArtist, strategy="random"):
    songList = []
    
    #---------first x method----------------
    if strategy == "first":
        #TODO: implement first x strategy for filtering playlists
        #loop through the items 
        #check if in artistDict
            #add each newly found artist to a dict with artist -> # of entries
            #found ones...
                #if over the maximum - remove the entry
                #else add 1 to value
        pass
    
    
    
    #--------random x method---------------
    elif strategy == "random":
        #loop through items
        #populate dict with artist -> [songs]
        for song in songs:
            artistName = song['artists'][0]['name']
            if artistName in artistDict.keys():
                #(make sure we don't have duplicate songs)
                if song not in artistDict[artistName]: 
                    artistDict[artistName].append(song)
            else:
                artistDict[artistName] = [song]
        
        #for each artist, check the number of songs, randomly choose maxSongsPerArtist to add to list
        for artist in artistDict:
            artistSongList = artistDict[artist]
            numSongs = len(artistSongList)
            if numSongs < maxSongsPerArtist:
                #less than max, so put in all songs
                songList += artistSongList
            else:
                #randomly select using sample function
                selection = list(sample(numSongs,maxSongsPerArtist))
                songList += list(artistSongList[i] for i in selection)

    #return the list
    return songList


def getSongList(playlistLength, callNo=0):
    #returns a list of track items, in order of most recently added
    #https://developer.spotify.com/web-api/object-model/#track-object-full

    #note: can only get maximum of 50 at a time

    global sp

    #keep track of the number of times we call this, so we can do the offset correctly
    if callNo == 0:
        offset = 0
    else:
        offset = callNo*min(playlistLength, 50)

    results = sp.current_user_saved_tracks(limit=min(playlistLength, 50), offset=offset)

    songsList = []
    #get rid of some of the extra info. Only have song objects
    for song in results['items']:
        songsList.append(song['track'])
    
    return songsList


def sample(n, r):
    #taken from http://code.activestate.com/recipes/272884-random-samples-without-replacement/
    #Generate r randomly chosen, sorted integers from [0,n)
    rand = random.random
    pop = n
    for samp in range(r, 0, -1):
        cumprob = 1.0
        x = rand()        
        while x < cumprob:
            cumprob -= cumprob * samp / pop
            pop -= 1
        yield n-pop-1


def createNewlyAddedPlaylist(playlistLength=50, maxSongsPerArtist=4, shuffle=False):
    global sp

    #get current user's id
    result = sp.current_user()
    userID = result['id']
    
    #get the current user's playlists (assumes less than 50)
    result = sp.current_user_playlists()
    playlists = result['items']

    #remove the old version of the playlist, if exists
    for playlist in playlists:
        if 'New Music [auto]' in playlist['name']:
            sp.user_playlist_unfollow(userID,playlist['id'])

    #create new playlist
    date = datetime.datetime.now()
    result = sp.user_playlist_create(userID, "New Music [auto] (" + date.strftime("%m/%d/%Y") + ")")
    newPlaylistID = result['id']

    #get most recent songs
    songs = getSongList(playlistLength)

    #filter the playlist to remove duplicate songs by artist (pass in empty dict)
    artistDict = {}
    songs = filterPlaylists(songs, artistDict, maxSongsPerArtist)

    #check to make sure at least playlistLength
    i = 1
    while len(songs) < playlistLength:
        #need more so ask spotify for more songs, filter (using dict), then append to list
        songs += getSongList(playlistLength, callNo=i)
        songs = filterPlaylists(songs, artistDict, maxSongsPerArtist)
        i += 1

    #truncate list
    songs = songs[0:playlistLength]

    #add all songs in list to playlist
    songIDs = []
    for song in songs:
        songIDs.append(song['id'])

    #shuffle the playlist if desired
    if shuffle:
        random.shuffle(songIDs)

    #commit songs to the playlist
    sp.user_playlist_add_tracks(userID, newPlaylistID, songIDs)
 

if __name__ == "__main__":
    #open up a new webpage tab for the localhost server (created next line)
    open_new_tab("http://localhost:5000")

    #run the flask server
    app.run()