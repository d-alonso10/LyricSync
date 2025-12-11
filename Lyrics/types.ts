export interface LyricLine {
  time: number; // Start time in seconds
  text: string;
}

export interface Song {
  id: string;
  title: string;
  artist: string;
  album: string;
  coverUrl: string;
  duration: number; // Total duration in seconds
  colorStart: string; // Gradient start color
  colorEnd: string; // Gradient end color
  lyrics: LyricLine[];
}

export interface PlayerState {
  isPlaying: boolean;
  currentTime: number;
}