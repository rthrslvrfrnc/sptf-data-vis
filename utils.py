import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = '8d4269eb20204e099376b858d6b97088'
CLIENT_SECRET = '797e6d6eb3824f82a6e74f01620cfba9'

# playlist_data_keys = ['track_position', 'track_name', 'spotify_id',
#                         'trck_number', 'artists', 'rtst_id', 'popularity',
#                         'duration_ms', 'album_name', 'album_id', 'album_release_date',
#                         'album_type', 'album_cover_url', 'is_explicit', 'genres']
playlist_data_keys = ['spotify_id', 'track_name', 'artists', 'snapshot_date', 'genres', 'country_name']
# playlist_data_keys = ['track_name',
#                       'spotify_id',
#                       'artists',
#                       'genres']

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_custom_playlist(playlist_id, playlist_name, enao):
  
  try:
    res = sp.playlist_tracks(playlist_id=playlist_id)
  except spotipy.SpotifyException:
    return pd.DataFrame()
  
  current_play_dt = {k: [] for k in playlist_data_keys}
  for pos, item in enumerate(res['items'], start=1):
    
    track = item['track']
    # album = track['album']
    artists = track['artists']
    
    rtst_name_list = [artist['name'] for artist in artists]
    rtst_id_list = [artist['id'] for artist in artists]
    
    rtsts_names = ", ".join(rtst_name_list)
    # rtsts_ids = ", ".join(rtst_id_list)
    
    a_res = sp.artist(rtst_id_list[0])
    genres = ", ".join(a_res['genres'])
    # ['spotify_id', 'track_name', 'artists', 'genres']
    # current_play_dt['track_position'].append(pos)
    current_play_dt['spotify_id'].append(track['id'])
    current_play_dt['track_name'].append(track['name'])
    
    # current_play_dt['trck_number'].append(track['track_number'])
    current_play_dt['artists'].append(rtsts_names)
    # current_play_dt['artist_id'].append(rtsts_ids)
    # current_play_dt['popularity'].append(track['popularity'])
    # current_play_dt['duration_ms'].append(track['duration_ms'])
    # current_play_dt['album_name'].append(album['name'])
    # current_play_dt['album_id'].append(album['id'])
    # current_play_dt['album_release_date'].append(album['release_date'])
    # current_play_dt['album_type'].append(album['album_type'])
    # current_play_dt['album_cover_url'].append(album['images'][0]['url'])
    # current_play_dt['is_explicit'].append(track['explicit'])
    current_play_dt['snapshot_date'].append('')
    current_play_dt['genres'].append(genres)
    current_play_dt['country_name'].append(playlist_name)
      
    
  df_myplaylist = pd.DataFrame.from_dict(current_play_dt)
  # playlist_gere_exp = df_myplaylist.assign(genres=df_myplaylist['genres'].str.split(', ')).explode('genres')
  # genre_counts = playlist_gere_exp['genres'].value_counts().reset_index()
  # genre_counts.columns = ['genre', 'song_count']
  # plot_data_enao = pd.merge(enao, genre_counts, on='genre', how='inner')
  # plot_data_enao['country'] = playlist_name
  
  return df_myplaylist