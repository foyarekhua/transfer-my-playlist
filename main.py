"""Fatimah Oyarekhua project 1:
Transfer music playlists to different platforms.
Supporting platforms include, youtube to spotify (for now).

steps:
step 1: log into youtube
step 2: find playlist we want to transfer
step 3: create a new spotify playlist
step 4: search for song and add it to new spotify playlist
step 5: repeat step 4 till all the songs have been iterated through
"""
import json
import requests

from personal_info import spotify_user_id, spotify_token

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl


class CreatePlaylist:
    def __init__(self):
        self.list_song_info = {}

    def get_source_client(self):
        """Logs into the source platform"""
        raise NotImplementedError

    def get_playlist(self):
        """Finds the playlist we want to transfer"""
        raise NotImplementedError

    def create_playlist(self) -> str:
        """Create a new playlist on the desired platform"""
        raise NotImplementedError

    def get_destination_uri(self, song_name: str, artist: str) -> str:
        """Find the uri of the song on the desired platform"""
        raise NotImplementedError

    def add_songs_to_playlist(self):
        """completes step 5 of adding the song to playlist"""
        raise NotImplementedError


class YoutubeToSpotify(CreatePlaylist):
    def __init__(self):
        super().__init__()
        self.user_id = spotify_user_id
        self.youtube_client = self.get_source_client()
        self.spotify_token = spotify_token

    def get_source_client(self):
        """completes step 1 and logs into youtube"""
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret_web.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)
        return youtube_client

    def get_playlist(self):
        """completes step 2 and finds the playlist we want to transfer"""

        playlist_url = input('insert playlist url: ')
        playlist_id = playlist_url[playlist_url.find('list=') + 5:]
        request = self.youtube_client.playlistItems().list(
            part="contentDetails,snippet",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()
        # response = list of videos
        for item in response['items']:
            video_title = item['snippet']['title']
            youtube_url = 'https://www.youtube.com/watch?v={}'.format(item['contentDetails']['videoId'])
            try:
                video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
                song_name = video['track']
                artist = video['artist']

                self.list_song_info[video_title] = {
                    'youtube_url': youtube_url,
                    'song_name': song_name,
                    'artist': artist,
                    'spotify_uri': self.get_destination_uri(song_name, artist)
                }
            except:
                self.list_song_info[video_title] = {
                    'youtube_url': youtube_url,
                    'song_name': 'NotFound',
                    'artist': 'NotFound',
                    'spotify_uri': 'N/A'
                }

    def create_playlist(self) -> str:
        """completes step 3 of creating a new playlist. Returns playlist ID of
        the new playlist
        """
        request_body = json.dumps({
            'name': 'YoutubeToSpotify',
            'description': 'Created by '
                           'transfer-my-playlist',
            'public': False
        })
        query = 'https://api.spotify.com/v1/users/{}/playlists'.format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(spotify_token)
            }

        )
        response_json = response.json()
        return response_json['id']

    def get_destination_uri(self, song_name: str, artist: str) -> str:
        """completes step 4 of finding the song"""
        query = 'https://api.spotify.com/v1/search?q=track%3A{}+artist%3A{}&type=track&offset=0&limit=20'.format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.spotify_token)
            }

        )
        response_json = response.json()
        songs = response_json['tracks']['items']

        # only use the first song
        uri = songs[0]['uri']
        return uri

    def add_songs_to_playlist(self):
        """completes step 5 of adding the song to playlist"""

        # create new playlist
        self.get_playlist()

        # collect all the songs in spotify format
        uris = []
        for song, info in self.list_song_info.items():
            if info['spotify_uri'] != 'N/A':
                uris.append(info['spotify_uri'])
            else:
                print('Can\'t find: ', str(song))

        playlist_id = self.create_playlist()

        # add songs
        request_data = json.dumps(uris)
        query = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id)
        response = requests.post(
            query,
            data=request_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.spotify_token)
            }
        )
        response_json = response.json()
        return response_json


class SpotifyToWatch2gether(CreatePlaylist):
    def __init__(self):
        super().__init__()
        self.spotify_token = spotify_token

    def get_playlist(self):
        playlist_url = input('insert playlist url: ')
        playlist_id = playlist_url[playlist_url.find('list/') + 5: playlist_url.find('?')]

        query = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id)

        response = requests.get(
            query,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.spotify_token)
            }

        )
        for i, song in enumerate(response.json()['items']):
            self.list_song_info['track {}'.format(i + 1)] = {
                'track': song['track']['name'],
                'artist': song['track']['artists'][0]['name']
                # TODO try to put multiple artists

            }



    def create_playlist(self) -> str:
        # TODO CURRENT ASSUMPTION: CREATE PLAYLIST RETURNS STREAMKEY
        pass


    def add_songs_to_playlist(self):
        # streamkey = self.create_playlist()
        # self.list_song_info = {
        #     "url": "https://www.youtube.com/watch?v=dMH0bHeiRNg",
        #     "title": "Hello World"}
        #
        # request_body = json.dumps({
        #     'w2g_api_key': placeholdertxt,  # TODO api key variable
        #     'add_items': [info for song, info in self.list_song_info.items()]
        # })
        #
        # query = "https://api.w2g.tv/rooms/{}/playlists/current/playlist_items/sync_update".format(
        #     streamkey)
        #
        # response = requests.post(
        #     query,
        #     data=request_body,
        #     headers={
        #         'Accept': 'application/json',
        #         'Content-Type': 'application/json'
        #     })


if __name__ == '__main__':
    # playlist_transfer = YoutubeToSpotify()
    # playlist_transfer.add_songs_to_playlist()

    playlist_transfer = SpotifyToWatch2gether()
    playlist_transfer.get_playlist()
