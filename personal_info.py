import webbrowser
import subprocess
# import os


redirect_uri = 'http%3A%2F%2Ftransfer-my-playlist%2Fcallback%2F'
spotify_client_id = 'INSERT_CLIENT_ID'
scopes = 'playlist-modify-public%20playlist-modify-private'
spotify_client_secret = 'iNSERT_CLIENT_SECRET'


def get_code():
    query = 'https://accounts.spotify.com/authorize?client_id={}&response_type=code&redirect_uri={}&scope={}'.format(
        spotify_client_id,
        redirect_uri,
        scopes
    )
    webbrowser.open(query)
    url = input('please input the url you were sent to:')
    codee = url[url.find('code=') + 5:]
    return codee


code = get_code()
curl = 'curl -H "Authorization: Basic ODM1NzIyNDFhMzE4NGQ5NDhhNTgzNmRjZWUwN2E5OWQ6MWJhNTg5ZGJjMmYzNGM5MjkxZWY5NDdlNzY3MTEwNjE=" -d grant_type=authorization_code -d code={} -d redirect_uri=http%3A%2F%2Ftransfer-my-playlist%2Fcallback%2F https://accounts.spotify.com/api/token --ssl-no-revoke'.format(code)
# os.system('cmd /c ' + '"' + curl + '"')
proc = subprocess.Popen(curl, shell=True, stdout=subprocess.PIPE)
serviceList = proc.communicate()[0]
serviceList = str(serviceList)
ac_tok_index_beg = serviceList.find('access_token":"') + 15
ac_tok_index_end = serviceList.find('"token_type') - 2
ref_tok_index_beg = serviceList.find('refresh_token":"') + 16
ref_tok_index_end = serviceList.find('"scope') - 2

spotify_token = serviceList[ac_tok_index_beg: ac_tok_index_end]
refresh_token = serviceList[ref_tok_index_beg: ref_tok_index_end]
spotify_user_id = input('please input your spotify username:')
