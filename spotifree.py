#!/usr/bin/env python3

import spotipy
import spotipy.util

import apiclient.discovery

import youtube_dl

import mutagen.mp3

import config

def addToCollection(title, artist):
  mp3file = mutagen.mp3.MP3('temp.mp3',ID3=mutagen.easyid3.EasyID3)
  mp3file['title'] = title
  mp3file['artist'] = artist
  mp3file.save()

def downloadSong(url):
  ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'temp.%(ext)s',
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
  results = sp.current_user_saved_tracks(1, offset)
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
  title = track['name']
  artist = track['artists'][0]['name']
  query = title + ' by ' + artist
  urls = youtubeSearch(query)
  for url in urls:
    downloadSong(url)
    addToCollection(title, artist)
