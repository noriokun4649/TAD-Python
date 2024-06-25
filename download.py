import os
import re
import requests
import yt_dlp
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

def get_existing_video_ids(directory):
    pattern = re.compile(r'\[v(\d+)\]\.mp4$')
    numbers = [pattern.search(file).group(1) for file in os.listdir(directory) if pattern.search(file)]
    return numbers


def fetch_twitch_video_ids(url, headers):
    response = requests.get(url, headers=headers)
    data = response.json()
    return [item['id'] for item in data['data']]


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


def stop_workers(executor):
    executor.shutdown(wait=False)
    print("すべてのWorkerを中止しました。")


download_dir = str(os.getenv('DL_DIR',os.path.join(os.getcwd(), 'Download')))
os.makedirs(download_dir, exist_ok=True)
os.chdir(download_dir)

existing_video_ids = get_existing_video_ids(download_dir)

url = f"https://api.twitch.tv/helix/videos?user_id={os.getenv('DL_USEE_ID')}&period=month&first=100"
headers = {
    'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
    'Authorization': f'Bearer {os.getenv("TWITCH_AUTH_TOKEN")}'
}

twitch_video_ids = fetch_twitch_video_ids(url, headers)

print("投稿されているアーカイブ一覧！！！")
print(twitch_video_ids)

new_video_ids = [video_id for video_id in twitch_video_ids if video_id not in existing_video_ids]

print("\n未ダウンロードのアーカイブ一覧！！！")
print(new_video_ids)
print(f"{len(new_video_ids)}個のアーカイブが未DL")

max_workers = int(os.getenv('MAX_WORKERS', 4))

print(f"\n{max_workers}スレッドで動画ダウンロード開始！！！")
download_videos_concurrently(new_video_ids, max_workers)

print("\nダウンロード終了！！！")
