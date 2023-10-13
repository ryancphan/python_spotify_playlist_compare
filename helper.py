import spotipy
from spotipy.oauth2 import SpotifyOAuth

def delete_if_exists(new_playlist_name, sp):
    # Check if the new playlist already exists
    new_playlist_id = Nonenew_playlist_id = None
    results = sp.current_user_playlists()
    while results:
        for playlist in results['items']:
            if playlist['name'] == new_playlist_name:
                new_playlist_id = playlist['id']
                break
        if new_playlist_id:
            break
        if results['next']:
            results = sp.next(results)
        else:
            results = None

    # If the new playlist already exists, delete it
    if new_playlist_id:
        sp.user_playlist_unfollow(sp.me()['id'], new_playlist_id)
        print(new_playlist_name + ' Overwritten')
        
def grab_tracks(playlist_id, sp):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    track_ids = [item['track']['id'] for item in tracks]
    return track_ids