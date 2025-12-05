import React, { useState, useEffect, useRef } from 'react';
import LyricsView from './components/LyricsView';
import WindowControls from './components/WindowControls';
import { Song } from './types';

const App: React.FC = () => {
  const [song, setSong] = useState<Song | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showSearch, setShowSearch] = useState<boolean>(true);

  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    const audio = new Audio();
    audio.crossOrigin = "anonymous";
    audioRef.current = audio;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const onEnded = () => setIsPlaying(false);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('ended', onEnded);

    return () => {
      audio.pause();
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('ended', onEnded);
    };
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`http://localhost:5001/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Failed to fetch song");

      const newSong: Song = {
        id: '1',
        title: data.title,
        artist: data.artist,
        album: "Unknown Album",
        coverUrl: data.cover_url || "https://picsum.photos/800/800",
        duration: data.duration,
        colorStart: "#4a148c", // We could extract colors from cover later
        colorEnd: "#1a237e",
        lyrics: data.lyrics
      };

      setSong(newSong);
      setShowSearch(false);

      if (audioRef.current) {
        audioRef.current.src = data.audio_url;
        audioRef.current.play().catch(e => console.error("Autoplay failed:", e));
        setIsPlaying(true);
      }

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const togglePlay = () => {
    if (!audioRef.current || !song) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  return (
    <div
      className="h-screen w-screen text-white flex flex-col relative overflow-hidden transition-colors duration-1000 select-none"
      style={{
        background: song
          ? `linear-gradient(160deg, ${song.colorStart} 0%, ${song.colorEnd} 100%)`
          : 'linear-gradient(160deg, #121212 0%, #000000 100%)'
      }}
    >
      <WindowControls />

      {/* Background Effects */}
      <div className="absolute inset-0 opacity-20 pointer-events-none"
        style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")` }}
      />
      <div className="absolute top-[-50%] left-[-50%] w-[200%] h-[200%] bg-gradient-to-br from-white/10 to-transparent rounded-full blur-3xl opacity-30 animate-pulse pointer-events-none" />

      {/* SEARCH OVERLAY */}
      {showSearch && (
        <div className="absolute inset-0 z-40 bg-black/80 backdrop-blur-md flex flex-col items-center justify-center p-6 no-drag">
          <h1 className="text-2xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500">
            VocaSync
          </h1>

          <form onSubmit={handleSearch} className="w-full">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search song..."
              className="w-full bg-white/10 border border-white/20 rounded-full px-4 py-3 text-sm text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
              autoFocus
            />
          </form>

          {isLoading && <div className="mt-4 text-green-400 text-sm animate-pulse">Downloading...</div>}
          {error && <div className="mt-4 text-red-400 text-xs text-center">{error}</div>}
        </div>
      )}

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col relative z-10 overflow-hidden" onClick={togglePlay}>
        {song ? (
          <LyricsView
            song={song}
            currentTime={currentTime}
            onSeek={handleSeek}
          />
        ) : (
          !showSearch && (
            <div className="flex-1 flex items-center justify-center opacity-50">
              <button onClick={() => setShowSearch(true)} className="text-sm hover:underline no-drag">
                Tap to Search
              </button>
            </div>
          )
        )}
      </div>

      {/* Search Toggle (Bottom Right) */}
      {!showSearch && (
        <button
          onClick={(e) => { e.stopPropagation(); setShowSearch(true); }}
          className="absolute bottom-4 right-4 z-50 p-2 bg-black/40 rounded-full hover:bg-black/60 transition-colors no-drag"
        >
          <svg className="w-4 h-4 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </button>
      )}
    </div>
  );
};

export default App;