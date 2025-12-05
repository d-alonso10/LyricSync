import React, { useEffect, useRef, useState } from 'react';
import { Song, LyricLine } from '../types';

interface LyricsViewProps {
  song: Song;
  currentTime: number;
  onSeek: (time: number) => void;
}

const LyricsView: React.FC<LyricsViewProps> = ({ song, currentTime, onSeek }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState<number>(0);


  useEffect(() => {
    let newIndex = 0;
    for (let i = 0; i < song.lyrics.length; i++) {
      if (currentTime >= song.lyrics[i].time) {
        newIndex = i;
      } else {
        break;
      }
    }
    setActiveIndex(newIndex);
  }, [currentTime, song.lyrics]);


  useEffect(() => {
    if (containerRef.current) {
      const activeElement = containerRef.current.children[activeIndex] as HTMLElement;
      if (activeElement) {
        activeElement.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      }
    }
  }, [activeIndex]);

  return (
    <div className="flex-1 w-full h-full relative overflow-hidden flex flex-col">
      <div className="absolute top-0 left-0 right-0 h-16 bg-gradient-to-b from-black/30 to-transparent z-10 pointer-events-none" />

      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto no-scrollbar py-[50vh] px-4 md:px-8 text-left no-drag"
      >
        {song.lyrics.map((line: LyricLine, index: number) => {
          const isActive = index === activeIndex;

          return (
            <div
              key={index}
              onClick={() => onSeek(line.time)}
              className={`
                transition-all duration-700 ease-[cubic-bezier(0.25,0.46,0.45,0.94)] 
                cursor-pointer origin-left my-4 md:my-6
                ${isActive
                  ? 'opacity-100 scale-100 translate-x-0'
                  : 'opacity-30 scale-95 hover:opacity-60'
                }
              `}
              style={{
                filter: isActive ? 'blur(0px)' : 'blur(1.5px)',
                transform: isActive ? 'scale(1)' : 'scale(0.98)',
              }}
            >
              <p className={`
                text-xl md:text-3xl font-bold leading-tight tracking-tight
                ${isActive ? 'text-white' : 'text-white'}
              `}>
                {line.text}
              </p>
            </div>
          );
        })}
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-black/50 to-transparent z-10 pointer-events-none" />
    </div>
  );
};

export default LyricsView;