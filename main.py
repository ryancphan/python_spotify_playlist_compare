import spotipy
from spotipy.oauth2 import SpotifyOAuth
from helper import delete_if_exists
from helper import grab_tracks

# Set your Spotify API credentials
client_id = 'be28a84c33d24c8fa027848728a49599'
client_secret = '2386a26ea164438f8c891a575c646e58'
redirect_uri = 'http://localhost:8888/callback'

# Authenticate with the Spotify API
scope = 'playlist-read-private playlist-modify-public playlist-modify-private'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                               redirect_uri=redirect_uri, scope=scope))

# Define the name of the master playlist
master_playlist_name = input("Enter master playlist:")

# Get the IDs of the playlists in the folder
playlist_ids = []
master_import_ids =[]
results = sp.current_user_playlists()
while results:
    for playlist in results['items']:
        if 'Import' in playlist['name']: # Grabs all playlists with the word Import
            if master_playlist_name in playlist['name']:
                master_import_ids.append(playlist['id'])
            else:
                playlist_ids.append(playlist['id'])
        if playlist['name'] == master_playlist_name: # Get the ID of the master playlist
            master_playlist_id = playlist['id']
        if playlist['name'] == 'Grab from Beatport':
            beatport_id = playlist['id']
    if results['next']:
        results = sp.next(results)
    else:
        results = None

# Add all the tracks in the selected playlists
other_tracks = []
for playlist_id in playlist_ids:
    track_ids = grab_tracks(playlist_id, sp)
    other_tracks += track_ids
    print(len(track_ids))

master_import_tracks = []
for playlist_id in master_import_ids:
    track_ids = grab_tracks(playlist_id, sp)
    master_import_tracks += track_ids

# Get the tracks in the master playlist
master_tracks = []
if master_playlist_id != '':
    master_tracks = grab_tracks(master_playlist_id, sp)

beatport_tracks = []
if beatport_id != '':
    beatport_tracks = grab_tracks(beatport_id, sp)

grab_count = 0
have_count = 0

for track in master_tracks:
    if track in other_tracks:
        have_count += 1
    else:
        grab_count += 1
        
print('tracks I have = ' + str(have_count))
print('Tracks to grab = ' + str(grab_count))

# Delete tracks already imported from the same playlist
master_tracks = list(set(master_tracks) - set(master_import_tracks))

# Create a new playlist with the tracks that are in the master playlist but not in any of the other playlists
new_playlist_name = 'Tracks to Grab'
delete_if_exists(new_playlist_name, sp)
new_playlist_description = 'New playlist with tracks from master playlist but not in any of the other playlists'
new_playlist_id = sp.user_playlist_create(sp.me()['id'], new_playlist_name, public=True, description=new_playlist_description)['id']
new_playlist_tracks = list(set(master_tracks) - set(other_tracks) - set(beatport_tracks))
if len(new_playlist_tracks) > 0:
    sp.playlist_add_items(new_playlist_id, new_playlist_tracks)

# Create a new playlist with the tracks that may already be in your music library
new_playlist_name2 = 'Tracks I have'
delete_if_exists(new_playlist_name2, sp)
new_playlist_description2 = 'New playlist with tracks that may already be in your music library'
new_playlist_id2 = sp.user_playlist_create(sp.me()['id'], new_playlist_name2, public=True, description=new_playlist_description2)['id']
new_playlist_tracks2 = list(set(master_tracks) - set(new_playlist_tracks) - set(beatport_tracks))
if len(new_playlist_tracks2) > 0:
    sp.playlist_add_items(new_playlist_id2, new_playlist_tracks2)

print('New playlist created with {} tracks!'.format(len(new_playlist_tracks)))

