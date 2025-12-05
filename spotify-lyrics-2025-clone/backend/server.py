import os
import re
import requests
import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures

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

    try:
        # Define helper functions for parallel execution
        def fetch_youtube_candidates(q):
            ydl_opts = {
                'format': 'bestaudio/best',
                'default_search': 'ytsearch10', # Increased from 5 to 10 for better variety
                'quiet': True,
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(q, download=False)
                if 'entries' in result:
                    return result['entries']
            return []

        def fetch_lyrics_candidates(q):
            session = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            session.mount('https://', HTTPAdapter(max_retries=retries))
            try:
                # Get more results to increase matching chances
                resp = session.get(f"https://lrclib.net/api/search?q={q}", timeout=5)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                print(f"Lyrics search error: {e}")
                return []

        # Execute searches in parallel
        video_candidates = []
        lyrics_candidates = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_yt = executor.submit(fetch_youtube_candidates, query)
            future_lyrics = executor.submit(fetch_lyrics_candidates, query)
            
            video_candidates = future_yt.result()
            lyrics_candidates = future_lyrics.result()

        if not video_candidates:
            return jsonify({"error": "Video not found"}), 404

        # SMART MATCHING ALGORITHM V2
        selected_video = None
        selected_lyrics = None
        
        # Filter usable lyrics
        valid_lyrics = [
            l for l in lyrics_candidates 
            if l.get('syncedLyrics') and l.get('duration')
        ]

        if not valid_lyrics:
             return jsonify({"error": "No synced lyrics found for this song"}), 404

        # Helper: Clean title for check
        def title_score(video_title):
            t = video_title.lower()
            if "audio" in t: return 2
            if "lyric" in t: return 1
            return 0

        # Pass 1: Strict Match (< 2s) - The Gold Standard
        # We prioritize videos that say "Audio" in title if matches are close
        best_diff = float('inf')
        
        for video in video_candidates:
            v_dur = video.get('duration')
            if not v_dur: continue
            
            for lyric in valid_lyrics:
                diff = abs(v_dur - lyric['duration'])
                
                if diff < 2.0:
                    # Found a great match. 
                    # If we already have a selected video, prefer the one with "Audio" in title
                    if selected_video and title_score(video['title']) > title_score(selected_video['title']):
                         selected_video = video
                         selected_lyrics = lyric['syncedLyrics']
                         best_diff = diff
                    elif not selected_video or diff < best_diff:
                         selected_video = video
                         selected_lyrics = lyric['syncedLyrics']
                         best_diff = diff
        
        # Pass 2: Relaxed Match (< 5s) - If Pass 1 failed
        if not selected_video:
            for video in video_candidates:
                v_dur = video.get('duration')
                if not v_dur: continue
                
                for lyric in valid_lyrics:
                    diff = abs(v_dur - lyric['duration'])
                    if diff < 5.0 and diff < best_diff:
                         selected_video = video
                         selected_lyrics = lyric['syncedLyrics']
                         best_diff = diff

        # Pass 3: Desperate Match (< 10s) - Only if Video explicitly says "Audio" or "Lyric"
        # Often official videos are way longer, but "Audio" versions might be just slightly off due to silence
        if not selected_video:
             for video in video_candidates:
                if title_score(video['title']) == 0: continue # Skip cinematic videos in this desperate pass
                
                v_dur = video.get('duration')
                if not v_dur: continue
                
                for lyric in valid_lyrics:
                    diff = abs(v_dur - lyric['duration'])
                    if diff < 10.0 and diff < best_diff:
                         selected_video = video
                         selected_lyrics = lyric['syncedLyrics']
                         best_diff = diff
        
        if not selected_video or not selected_lyrics:
            return jsonify({
                "error": f"Could not find a synchronized match. Best diff: {best_diff if best_diff != float('inf') else 'N/A'}s"
            }), 404

        # Set variables for download
        video_title = selected_video.get('title')
        video_duration = selected_video.get('duration')
        video_url = selected_video.get('url')
        video_id = selected_video.get('id')
        lrc_content = selected_lyrics
        video_info = selected_video


        # Download MP3 (Optimized)
        filename = f"{video_id}.mp3"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            ydl_download = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, video_id),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128', # Reduced from 192 for speed
                }],
                'quiet': True,
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(ydl_download) as ydl:
                ydl.download([video_url])
        
        parsed_lyrics = parse_lrc(lrc_content)
        
        return jsonify({
            "title": video_title,
            "artist": "Unknown", 
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
