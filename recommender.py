import pickle
import pandas as pd
import spotipy
from flask import Flask, request, jsonify, render_template

#connection to Spotify Web api
from spotipy.oauth2 import SpotifyClientCredentials
secrets_file = open("spotifyclientkevin.txt","r")
string = secrets_file.read()
secrets_dict={}
for line in string.split('\n'):
    if len(line) > 0:
        #print(line.split(':'))
        secrets_dict[line.split(':')[0]]=line.split(':')[1].strip()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=secrets_dict['clientid'],
                                                           client_secret=secrets_dict['clientsecret']))

#load model
with open('kmeans_model_20clusters.pkl', 'rb') as file:
    kmeans = pickle.load(file)

#load scaler
with open('scaler_minmax.pkl', 'rb') as file:
    scaler = pickle.load(file)

#load library
our_library = pd.read_csv('our_library.csv')

def ms_to_mm_ss(ms): # a small converter turning miliseconds into 'minute:seconds' time display format
    seconds = ms // 1000
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02}:{seconds:02}"

#-------------------------------------------------------- Query Song info retriever -------------------------------------------------------
def search_song(song):
    query = str(song)
    searched_song = sp.search(q=query, limit=1)
    
    searched_song_name = searched_song['tracks']['items'][0]['name']
    searched_song_artist = searched_song['tracks']['items'][0]['artists'][0]['name']
    searched_song_album = searched_song['tracks']['items'][0]['album']['name']
    searched_song_length_ms = searched_song['tracks']['items'][0]['duration_ms']
    searched_song_length_mm_ss = ms_to_mm_ss(searched_song_length_ms)
    searched_song_release_date = searched_song['tracks']['items'][0]['album']['release_date']
    searched_song_cover_image = searched_song['tracks']['items'][0]['album']['images'][0]['url']
    searched_song_id = searched_song['tracks']['items'][0]['id']
    
    servo_dictionary = {'name':searched_song_name,
                        'artist':searched_song_artist,
                        'album':searched_song_album,
                        'length_ms':searched_song_length_ms,
                        'mm_ss':searched_song_length_mm_ss,
                        'release_date':searched_song_release_date,
                        'cover_image':searched_song_cover_image,
                        'song_id':searched_song_id}
    return servo_dictionary

#--------------------------------------------------------Song Feature retriever -------------------------------------------------------

def retrive_pred_feature(song):    
    featdf = pd.DataFrame(sp.audio_features(search_song(song)['song_id']))
    resdf = featdf[['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo']]
    return resdf

#---------------------------------------------------------Cluster recommender--------------------------------------------------------

def cluster_recommend(song, n=5):
    from random import sample
    song_features = retrive_pred_feature(song)
    
    X_pred = scaler.transform(song_features)
    
    res_cluster = kmeans.predict(X_pred) # the result cluster (just a number) for the input song is here
    
    same_cluster_songs = our_library[our_library['cluster'] == res_cluster[0]].reset_index(drop=True) # gets dataframe of all songs in same cluster

    randindex_list = sample(list(range(len(same_cluster_songs))),n)
    output_songs = same_cluster_songs.iloc[randindex_list]
    
    output = output_songs[['song_name','name','song_id']]
    #print('|Song:|  '+output[0]+'  |Artist:|  '+output[1])
    
    return output

#---------------------------------------------------------Output Compiling-------------------------------------------------------

def recommender(x=None):
    #if x == None:
    #    song = input('Enter a song to hear our recommendation: ')
    #else:
    #    song = x

    if x is None:
        raise ValueError("No song provided for recommendation.")  # Handle missing input gracefully

    song = x

    output_dictionary = {}
    
    song_name = str(song).lower() #This makes all the input a lowercase string value, as far as I am concerned, this should not cause any problem and makes it convenient for comparison
    returned_tracks = cluster_recommend(song_name)
    output_dictionary['searched_song'] = search_song(song)
    
    tracks_info = sp.tracks(returned_tracks['song_id'])#Another call to spotify api to get track info for recommended songs
    servo_list = []
    for track in tracks_info['tracks']:
            name = track['name']
            artist = track['artists'][0]['name']
            album = track['album']['name']
            length_ms = track['duration_ms']
            length_mm_ss = ms_to_mm_ss(length_ms)
            release_date = track['album']['release_date']
            cover_image = track['album']['images'][0]['url']
            song_id = track['id']

            servo_list.append({'name':name,
                                'artist':artist,
                                'album':album,
                                'length_ms':length_ms,
                                'mm_ss':length_mm_ss,
                                'release_date':release_date,
                                'cover_image':cover_image,
                                'song_id':song_id})
    
    output_dictionary['recommended_songs'] = servo_list
        
    return output_dictionary

recommender()


#---------------------------------------------------------SERVER CONFIG-------------------------------------------------------


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML page

@app.route('/history')
def history():
    return render_template('history.html')  # Serve the HTML page


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    #data = request.data.decode('utf-8')  # Get the input data as a plain string
    recommendations = recommender(data)  # Call your recommender function
    return jsonify({
        "status": "success",
        "recommendations": recommendations
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)