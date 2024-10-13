import os
import re
import requests
import yt_dlp
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

def get_existing_video_ids(directory):
    pattern = re.compile(r'\[v(\d+)\]\.mp4$')
    numbers = [pattern.search(file).group(1) for file in os.listdir(directory) if pattern.search(file)]
    return numbers

def fetch_user_id(username, headers):
    url = f"https://api.twitch.tv/helix/users?login={username}"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data'][0]['id']


def fetch_user_name(user_id, headers):
    url = f"https://api.twitch.tv/helix/users?id={user_id}"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data'][0]['display_name']


def fetch_twitch_video_ids(url, headers):
    video_ids = []
    baseurl = url
    while True:
        response = requests.get(url, headers=headers)
        data = response.json()
        video_ids.extend([item['id'] for item in data['data'] if 'vod-secure.twitch.tv/_404/404_processing_' not in item['thumbnail_url']])
        cursor = data.get('pagination', {}).get('cursor')
        if cursor:
            url = f"{baseurl}&after={cursor}"
        else:
            break
    return video_ids


def download_video(video_id):
    ydl_opts = {
                    'format': 'best',
                    'cookiefile': os.getenv('COOKIE_FILE', os.path.join(os.getcwd(), 'cookiefile'))
                }
    video_url = f'https://www.twitch.tv/videos/{video_id}'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def download_videos_concurrently(video_ids, max_workers):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(download_video, video_ids)


def fetch_oauth_token():
    url = "https://id.twitch.tv/oauth2/token"
    clinet_id = os.getenv('TWITCH_CLIENT_ID')
    client_secret = os.getenv('TWITCH_CLIENT_SECRET')
    url = url + f"?client_id={clinet_id}&client_secret={client_secret}&grant_type=client_credentials"
    response = requests.post(url=url)
    data = response.json()
    return data["access_token"]


def init():
    userid = os.getenv('DL_USER_ID')
    client_id = os.getenv('TWITCH_CLIENT_ID')
    download_dir = os.getenv('DL_DIR',os.path.join(os.getcwd(), 'Download'))
    auth_token = fetch_oauth_token()
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {auth_token}'
    }

    if userid == None:
        print("UserIDが空です")
        return

    if not userid.isdigit():
        userid = fetch_user_id(userid, headers)

    os.makedirs(download_dir, exist_ok=True)
    os.chdir(download_dir)

    existing_video_ids = get_existing_video_ids(download_dir)

    url = f"https://api.twitch.tv/helix/videos?user_id={userid}&first=100"


    twitch_video_ids = fetch_twitch_video_ids(url, headers)
    user_name = fetch_user_name(userid, headers)

    print(f"{user_name}({userid})のダウンロード開始！！！ [{datetime.now()}]")

    print(f"\n投稿されているアーカイブ一覧！！！{len(twitch_video_ids)}個！")
    print(twitch_video_ids)

    new_video_ids = [video_id for video_id in twitch_video_ids if video_id not in existing_video_ids]

    if len(new_video_ids) < 1:
        print("未ダウンロードのアーカイブ無し！！！")
        return

    print(f"\n未ダウンロードのアーカイブ一覧！！！{len(new_video_ids)}個！")
    print(new_video_ids)
    print(f"{len(new_video_ids)}個のアーカイブが未DL")

    max_workers = int(os.getenv('MAX_WORKERS', 4))

    print(f"\n{max_workers}スレッドで動画ダウンロード開始！！！")
    download_videos_concurrently(new_video_ids, max_workers)

    print("\nダウンロード終了！！！\n--------------------------\n")


if __name__ == "__main__":
    load_dotenv()
    init()