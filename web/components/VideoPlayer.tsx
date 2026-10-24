"use client";

import React from "react";
import { getVideoDownloadUrl } from "../lib/api";

interface VideoPlayerProps {
  jobId: string;
  videoUrl?: string | null;
  onReset: () => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ jobId, videoUrl, onReset }) => {
  const resolvedUrl = videoUrl || getVideoDownloadUrl(jobId);

  return (
    <div className="w-full max-w-4xl bg-[#0D0F14] border border-white/10 rounded-2xl overflow-hidden shadow-2xl space-y-6 p-6">
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <span className="text-xs uppercase font-semibold tracking-widest text-emerald-400">
            RENDER COMPLETE
          </span>
          <h2 className="text-3xl font-headline text-white mt-1 uppercase">
            YOUR PRODUCT LAUNCH FILM
          </h2>
        </div>
        <div className="flex gap-2">
          <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-slate-300 font-mono">
            1080P • 30 FPS
          </span>
          <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs text-blue-400 font-mono">
            H.264 MP4
          </span>
        </div>
      </div>

      {/* HTML5 Video Player */}
      <div className="aspect-video w-full rounded-xl overflow-hidden bg-black border border-white/10 shadow-inner relative flex items-center justify-center">
        <video
          key={resolvedUrl}
          src={resolvedUrl}
          controls
          autoPlay
          muted
          playsInline
          loop
          className="w-full h-full object-cover"
        />
      </div>

      {/* Action Controls */}
      <div className="flex flex-col sm:flex-row items-center gap-4 pt-2">
        <a
          href={resolvedUrl}
          download={`launch-${jobId.slice(0, 8)}.mp4`}
          className="w-full sm:w-auto flex-1 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-headline text-2xl tracking-wide rounded-xl uppercase transition text-center shadow-lg shadow-emerald-600/20"
        >
          DOWNLOAD 1080P MP4
        </a>
        <button
          onClick={onReset}
          className="w-full sm:w-auto px-8 py-4 bg-white/5 hover:bg-white/10 text-slate-300 font-headline text-2xl tracking-wide rounded-xl uppercase transition border border-white/10"
        >
          GENERATE ANOTHER
        </button>
      </div>
    </div>
  );
};
