import os
import re
import requests
import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)
CORS(app)

# Configuration
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

TOLERANCIA_SEGUNDOS = 5.0

def parse_lrc(lrc_content):
    lyrics = []
    # Regex to capture timestamp and text
    # Supports [mm:ss.xx] or [mm:ss.xxx]
    lrc_regex = re.compile(r'\[(\d{2}):(\d{2})\.?(\d{2,3})?\](.*)')
    
    lines = lrc_content.split('\n')
    for line in lines:
        match = lrc_regex.match(line)
        if not match: continue
        
        minutos = int(match.group(1))
        segundos = int(match.group(2))
        frac_str = match.group(3) if match.group(3) else "0"
        
        # Normalize milliseconds
        if len(frac_str) == 2:
            frac_seg = int(frac_str) * 10
        else:
            frac_seg = int(frac_str)
            
        texto = match.group(4).strip()
        
        # Calculate total seconds for the frontend
        total_seconds = (minutos * 60) + segundos + (frac_seg / 1000)
        
        if texto:
            lyrics.append({
                "time": total_seconds,
                "text": texto
            })
            
    lyrics.sort(key=lambda x: x["time"])
    return lyrics

@app.route('/search', methods=['GET'])
def search_song():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    print(f"Searching for: {query}")
    
    try:
        # 1. Search YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch1',
            'quiet': True,
            'noplaylist': True,
        }
        
        video_info = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)
            if 'entries' in result and len(result['entries']) > 0:
                video_info = result['entries'][0]
        
        if not video_info:
            return jsonify({"error": "Video not found"}), 404
            
        video_duration = video_info.get('duration')
        video_title = video_info.get('title')
        video_url = video_info.get('url')
        video_id = video_info.get('id')
        
        print(f"Found Video: {video_title} ({video_duration}s)")

        # 2. Search Lyrics
        lrc_content = None
        
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        try:
            resp = session.get(f"https://lrclib.net/api/search?q={query}", timeout=10)
            resp.raise_for_status()
            results = resp.json()
            
            for item in results:
                if not item.get('syncedLyrics') or not item.get('duration'):
                    continue
                
                if abs(item['duration'] - video_duration) <= TOLERANCIA_SEGUNDOS:
                    lrc_content = item['syncedLyrics']
                    print("Found synced lyrics!")
                    break
        except Exception as e:
            print(f"Lyrics search error: {e}")
            
        if not lrc_content:
            return jsonify({"error": "Lyrics not found for this song version"}), 404

        # 3. Download MP3
        filename = f"{video_id}.mp3"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            print("Downloading MP3...")
            ydl_download = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, video_id),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_download) as ydl:
                ydl.download([video_url])
        
        # 4. Parse Lyrics
        parsed_lyrics = parse_lrc(lrc_content)
        
        return jsonify({
            "title": video_title,
            "artist": "Unknown", # YouTube doesn't always give clean artist
            "duration": video_duration,
            "lyrics": parsed_lyrics,
            "audio_url": f"http://localhost:5001/stream/{filename}",
            "cover_url": video_info.get('thumbnail')
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stream/<filename>')
def stream_audio(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(port=5001, debug=True)
