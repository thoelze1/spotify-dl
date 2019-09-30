#!/usr/bin/env python3

import spotipy
import spotipy.util

import apiclient.discovery

import youtube_dl

import config

def downloadSong(url):
  ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
  }
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

def youtubeSearch(query):
  youtube = apiclient.discovery.build('youtube','v3',developerKey=config.dev_key)
  search_response = youtube.search().list(maxResults=1,part="id,snippet",q=query).execute()
  urls = []
  for search_result in search_response.get("items", []):
      if search_result["id"]["kind"] == "youtube#video":
          urls.append("%s" % ("http://youtu.be/" + search_result["id"]["videoId"]))
  return urls

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
  results = sp.current_user_saved_tracks(5, offset)
  library = results
  '''
  while len(results['items']) == 20:
    offset += 20
    results = sp.current_user_saved_tracks(20, offset)
    library['items'] += results['items']
  '''
  return library

library = getLibrary()

for item in library['items']:
  track = item['track']
  query = track['name'] + ' by ' + track['artists'][0]['name']
  urls = youtubeSearch(query)
  for url in urls:
    downloadSong(url)
