# TAD-Python
Twitch Arcive Downloader for Python

# TwitchAPI settings
```
cp .env.sample .env
```

.env
```ini
TWITCH_CLIENT_ID= #ClientIDを記入
TWITCH_AUTH_TOKEN= #Tokenを記入
DL_USEE_ID= #DL対象のUserID
MAX_WORKERS=4 # DLを実行するWorkerの数　任意
```

# run
```
pip install -r requirements.txt
python download.py
```