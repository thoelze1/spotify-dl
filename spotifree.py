#!/usr/bin/env python3

import spotipy
import spotipy.util

import config

def getLibrary():
  token = spotipy.util.prompt_for_user_token(
            config.username,
            'user-library-read',
            config.client_id,
            config.client_secret,
            config.redirect_uri)
  if not token:
    print("Can't get token for %s" % config.username)
    return None
  sp = spotipy.Spotify(auth=token)
  offset = 0
  results = sp.current_user_saved_tracks(20, offset)
  library = results
  while len(results['items']) == 20:
    offset += 20
    results = sp.current_user_saved_tracks(20, offset)
    library['items'] += results['items']
  return library

library = getLibrary()

for item in library['items']:
    track = item['track']
    print(track['name'] + ' - ' + track['artists'][0]['name'])
