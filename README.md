# VocaSync 🎶

A dynamic Python console app that fetches audio from YouTube and displays perfectly synced lyrics, right in your terminal. 

Turn your console into a real-time lyric-syncing machine. VocaSync automatically searches for any song, downloads the best-matched audio from YouTube, and finds its corresponding timed `.lrc` lyrics. It then intelligently validates both sources by comparing their duration to ensure a perfect sync.


---

## 🚀 Features

* **Search On-Demand:** Just type the song name and artist.
* **Smart Matching:** Downloads YouTube audio and validates it against the duration of the best-matched `.lrc` lyric file. No more sync issues with "official music videos" vs. "studio audio".
* **Dynamic Console UI:** A clean, Spotify-like "now playing" interface that highlights the current lyric and fades out past and future lines.
* **Automatic Cleanup:** No setup needed. It downloads temporary `mp3` and `lrc` files and overwrites them on the next search.
* **Cross-Platform:** Works on Windows, macOS, and Linux.

---

## 🛠️ Requirements

Before you begin, you **must** have these installed:

1.  **Python 3.10+**
2.  **FFmpeg:** This is critical for converting the audio file.
    * **Windows:** Download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/) (get the `essentials` build), unzip it, and [add the `bin` folder to your system's PATH](https://www.architectryan.com/2018/03/17/add-to-windows-path-with-powershell/).
    * **macOS (via Homebrew):** `brew install ffmpeg`
    * **Linux (via apt):** `sudo apt update && sudo apt install ffmpeg`
3.  **Pip** (Python's package installer)

---

## ⚙️ Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/TU_USUARIO/VocaSync.git](https://github.com/TU_USUARIO/VocaSync.git)
    cd VocaSync
    ```

2.  **Create a `requirements.txt` file** with the following content:
    ```txt
    pygame
    colorama
    requests
    yt-dlp
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    
4.  **Run the script!**
    * **Modo Interactivo:**
        ```bash
        python karaoke.py
        ```
        (El script te preguntará qué canción quieres).

    * **Modo Rápido (con argumentos):**
        ```bash
        python karaoke.py "michael jackson billie jean"
        ```
        
> **Nota:** ¡Considera renombrar `karaoke.py` a `main.py` o `vocasync.py` para que se vea más profesional!

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
