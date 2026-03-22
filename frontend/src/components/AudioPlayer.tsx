"use client";

import { useState, useRef, useEffect } from "react";

export default function AudioPlayer({ src }: { src: string }) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const rates = [1, 1.25, 1.5, 2];

  useEffect(() => {
    // When the component unmounts or src changes, pause current playback
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, [src]);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const skip = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime += seconds;
    }
  };

  const cyclePlaybackRate = () => {
    if (audioRef.current) {
      const nextIdx = (rates.indexOf(playbackRate) + 1) % rates.length;
      const nextRate = rates[nextIdx];
      audioRef.current.playbackRate = nextRate;
      setPlaybackRate(nextRate);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setProgress(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = value;
      setProgress(value);
    }
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return "0:00";
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  return (
    <div className="mt-2 rounded-xl border border-stone-800 bg-stone-900/80 p-4 shadow-sm">
      <audio
        ref={audioRef}
        src={src}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
      />
      
      {/* Progress Bar */}
      <div className="mb-4 flex items-center gap-3">
        <span className="w-12 text-right text-xs text-stone-400 font-mono">
          {formatTime(progress)}
        </span>
        <input
          type="range"
          min="0"
          max={duration || 100}
          value={progress}
          onChange={handleSeek}
          className="flex-1 h-1.5 cursor-pointer appearance-none rounded-full bg-stone-700 accent-amber-500 hover:accent-amber-400 focus:outline-none"
          title="Seek progression"
        />
        <span className="w-12 text-xs text-stone-400 font-mono">
          {formatTime(duration)}
        </span>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-4">
        {/* Playback speed */}
        <button
          onClick={cyclePlaybackRate}
          className="flex items-center justify-center w-12 h-8 rounded-lg bg-stone-700/50 text-xs font-semibold tracking-wider text-amber-500 hover:bg-stone-600 transition-colors"
          title="Playback speed"
        >
          {playbackRate}x
        </button>

        {/* Back 5s */}
        <button
          onClick={() => skip(-5)}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-stone-800 text-stone-300 hover:bg-stone-700 hover:text-white transition-all transform hover:scale-105"
          title="Back 5 seconds"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
          </svg>
        </button>

        {/* Play / Pause */}
        <button
          onClick={togglePlay}
          className="flex items-center justify-center w-14 h-14 rounded-full bg-amber-500 text-stone-900 hover:bg-amber-400 shadow-md transition-all transform hover:scale-105"
          title={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? (
            <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-7 h-7 ml-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
            </svg>
          )}
        </button>

        {/* Skip 5s */}
        <button
          onClick={() => skip(5)}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-stone-800 text-stone-300 hover:bg-stone-700 hover:text-white transition-all transform hover:scale-105"
          title="Skip 5 seconds"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
          </svg>
        </button>

        {/* Spacer to perfectly center the Play button visually despite the 1x button on the left */}
        <div className="w-12"></div>
      </div>
    </div>
  );
}
