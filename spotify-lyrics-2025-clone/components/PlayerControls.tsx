import React from 'react';
import { Song } from '../types';
import { PlayIcon, PauseIcon, SkipBackIcon, SkipForwardIcon, ShuffleIcon, RepeatIcon } from './Icons';

interface PlayerControlsProps {
  song: Song;
  isPlaying: boolean;
  currentTime: number;
  onTogglePlay: () => void;
  onSeek: (time: number) => void;
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const PlayerControls: React.FC<PlayerControlsProps> = ({ 
  song, 
  isPlaying, 
  currentTime, 
  onTogglePlay, 
  onSeek 
}) => {
  const progressPercent = (currentTime / song.duration) * 100;

  return (
    <div className="w-full h-24 md:h-28 glass-panel border-t border-white/10 px-4 md:px-8 flex items-center justify-between z-50">
      
      {/* Song Info (Left) */}
      <div className="flex items-center gap-4 w-1/4 min-w-[150px]">
        <img 
          src={song.coverUrl} 
          alt="Album Art" 
          className="w-14 h-14 rounded-md shadow-lg object-cover hidden md:block"
        />
        <div className="flex flex-col justify-center overflow-hidden">
          <span className="text-white font-bold text-sm md:text-base truncate">{song.title}</span>
          <span className="text-gray-400 text-xs md:text-sm truncate hover:underline cursor-pointer hover:text-white transition-colors">{song.artist}</span>
        </div>
      </div>

      {/* Center Controls (Playback + Progress) */}
      <div className="flex flex-col items-center justify-center flex-1 max-w-2xl px-4">
        
        {/* Buttons */}
        <div className="flex items-center gap-6 mb-2">
            <button className="text-gray-400 hover:text-white transition-colors">
                <ShuffleIcon className="w-5 h-5" />
            </button>
            <button 
                className="text-gray-300 hover:text-white transition-colors"
                onClick={() => onSeek(Math.max(0, currentTime - 5))} // Rewind 5s
            >
                <SkipBackIcon className="w-6 h-6" />
            </button>
            
            <button 
                onClick={onTogglePlay}
                className="bg-white text-black rounded-full p-2 hover:scale-105 transition-transform active:scale-95 shadow-xl"
            >
                {isPlaying ? <PauseIcon className="w-8 h-8" /> : <PlayIcon className="w-8 h-8 pl-1" />}
            </button>

            <button 
                className="text-gray-300 hover:text-white transition-colors"
                onClick={() => onSeek(Math.min(song.duration, currentTime + 5))} // Skip 5s
            >
                <SkipForwardIcon className="w-6 h-6" />
            </button>
            <button className="text-green-500 hover:text-green-400 transition-colors">
                <RepeatIcon className="w-5 h-5" />
            </button>
        </div>

        {/* Progress Bar */}
        <div className="w-full flex items-center gap-3 text-xs font-medium text-gray-400">
          <span className="min-w-[40px] text-right">{formatTime(currentTime)}</span>
          
          <div className="relative flex-1 h-1.5 bg-gray-600/50 rounded-full cursor-pointer group group/slider">
            <div 
              className="absolute top-0 left-0 h-full bg-white rounded-full transition-all duration-100 group-hover/slider:bg-green-500"
              style={{ width: `${progressPercent}%` }}
            >
                {/* Thumb appears on hover */}
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover/slider:opacity-100 shadow-md transform translate-x-1/2" />
            </div>
            
            <input 
              type="range" 
              min={0} 
              max={song.duration} 
              value={currentTime}
              onChange={(e) => onSeek(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </div>
          
          <span className="min-w-[40px]">{formatTime(song.duration)}</span>
        </div>
      </div>

      {/* Right Controls (Volume/Misc) - Placeholder for visual balance */}
      <div className="w-1/4 hidden md:flex items-center justify-end gap-2 text-gray-400">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
          <svg className="w-5 h-5 ml-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
      </div>

    </div>
  );
};

export default PlayerControls;