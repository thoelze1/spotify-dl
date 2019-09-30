#!/usr/bin/env python3

import spotipy
import spotipy.util

import apiclient.discovery

import youtube_dl

import mutagen.mp3

import urllib.request

import os

import config

def downloadArt(track):
  images = track['album']['images']
  maxh = 0
  bestimg = 0
  for image in images:
    if image['height'] > maxh:
      maxh = image['height']
      bestimg = image
  urllib.request.urlretrieve(bestimg['url'], 'temp.jpg')

def addToCollection(title, artist, album):
  mp3file = mutagen.mp3.MP3('temp.mp3',ID3=mutagen.id3.ID3)
  mp3file.tags.add(
    mutagen.id3.TIT2(
      encoding=3,
      text=title
    )
  )
  mp3file.tags.add(
    mutagen.id3.TPE1(
      encoding=3,
      text=artist
    )
  )
  mp3file.tags.add(
    mutagen.id3.TALB(
      encoding=3,
      text=album
    )
  )
  mp3file.tags.add(
    mutagen.id3.APIC(
        encoding=3, # 3 is for utf-8
        mime='image/jpeg', # image/jpeg or image/png
        type=3, # 3 is for the cover image
        desc=u'Cover',
        data=open('temp.jpg','rb').read()
    )
  )
  mp3file.save()
  path = 'music/' + artist + '/' + album
  if not os.path.exists(path):
    os.makedirs(path)
  os.rename('temp.mp3', path + '/' + title + '.mp3')

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
  search_response = youtube.search().list(maxResults=4,part="id,snippet",q=query).execute()
  urls = []
  for search_result in search_response.get("items", []):
      if search_result["id"]["kind"] == "youtube#video":
          urls.append("%s" % ("http://youtu.be/" + search_result["id"]["videoId"]))
  return urls[0]

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
  results = sp.current_user_saved_tracks(10, offset)
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
  album = track['album']['name']
  query = title + ' by ' + artist
  url = youtubeSearch(query)
  downloadSong(url)
  downloadArt(track)
  addToCollection(title, artist, album)
