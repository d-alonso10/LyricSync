# LyricSync 🎵

**LyricSync** is a modern, floating lyrics widget that brings your karaoke experience to life. It combines a beautiful **Electron/React** frontend with a powerful **Python** backend to fetch, sync, and display lyrics in real-time.

<img width="788" height="306" alt="image" src="https://github.com/user-attachments/assets/822b01fd-9526-408a-b15e-ede6db9d63fd" />


<img width="288" height="286" alt="image" src="https://github.com/user-attachments/assets/55d1015a-fc98-4edf-93ed-2f3d390803b7" />
<img width="323" height="291" alt="image" src="https://github.com/user-attachments/assets/a3b2ed7b-0a72-43c0-a6b1-45910179cdfd" />


---

## ✨ Features

*   **Floating Widget:** A transparent, always-on-top window that sits perfectly on your screen.
*   **Smart Sync:** Automatically searches, downloads, and syncs lyrics from multiple sources (LRCLIB, Netease, etc.).
*   **Stunning UI:** Features dynamic gradients, smooth scrolling, and a polished, Spotify-inspired design.
*   **Hybrid Power:** Leverages the flexibility of web technologies (React) with the raw processing power of Python.
*   **Drag & Drop:** Easily move the widget anywhere on your screen.

---

## 🛠️ Prerequisites

Ensure you have the following installed on your system:

1.  **Node.js** (v18 or higher)
2.  **Python** (v3.10 or higher)
3.  **FFmpeg** (Required for audio processing)
    *   *Windows:* Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract, and add `bin` to your PATH.

---

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/LyricSync.git
    cd LyricSync
    ```

2.  **Install Backend Dependencies:**
    ```bash
    cd Lyrics/backend
    pip install -r requirements.txt
    ```

3.  **Install Frontend Dependencies:**
    ```bash
    cd ../  # Go back to 'Lyrics' folder
    npm install
    ```

---

## ▶️ How to Run

### 🌟 Silent Mode (Production)
For the best experience (no terminal windows), use the silent launcher:

1.  Navigate to the `Lyrics` folder.
2.  Double-click **`LyricSync_Silent.vbs`**.

*Tip: You can create a Desktop Shortcut to this file and give it the `app-icon.png` for a professional look.*

### 👨‍💻 Developer Mode
If you want to see the logs and terminals for debugging:

1.  Navigate to the `Lyrics` folder.
2.  Double-click **`start_app.bat`**.

Alternatively, you can run the components manually:

*   **Backend:** `python server.py` (inside `Lyrics/backend`)
*   **Frontend:** `npm run electron:dev` (inside `Lyrics`)

---

## 🏗️ Architecture

*   **Frontend:** React, Vite, TailwindCSS, Electron.
*   **Backend:** Python, Flask, yt-dlp.
*   **Communication:** REST API (The frontend requests song data from `http://localhost:5001`).

---

## 📄 License

This project is licensed under the MIT License.
