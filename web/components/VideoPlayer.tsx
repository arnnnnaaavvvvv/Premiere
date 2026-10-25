"use client";

import React, { useState } from "react";
import { getVideoDownloadUrl } from "../lib/api";

interface VideoPlayerProps {
  jobId: string;
  videoUrl?: string | null;
  onReset: () => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ jobId, videoUrl, onReset }) => {
  const resolvedUrl = videoUrl || getVideoDownloadUrl(jobId);
  const [activeTab, setActiveTab] = useState<"generated" | "reference">("generated");

  return (
    <div className="w-full max-w-4xl bg-[#0D0F14] border border-white/10 rounded-2xl overflow-hidden shadow-2xl space-y-6 p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs uppercase font-semibold tracking-widest text-emerald-400">
              NOTION-STYLE RENDER COMPLETE
            </span>
          </div>
          <h2 className="text-3xl font-headline text-white mt-1 uppercase">
            YOUR PRODUCT LAUNCH FILM
          </h2>
        </div>

        {/* View Tabs */}
        <div className="flex items-center gap-2">
          <div className="flex p-1 bg-white/5 border border-white/10 rounded-xl">
            <button
              onClick={() => setActiveTab("generated")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
                activeTab === "generated"
                  ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Your Launch Film
            </button>
            <button
              onClick={() => setActiveTab("reference")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
                activeTab === "reference"
                  ? "bg-purple-600 text-white shadow-md shadow-purple-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Reference Style
            </button>
          </div>
        </div>
      </div>

      {/* Video Canvas Area */}
      {activeTab === "generated" ? (
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
      ) : (
        <div className="space-y-2">
          <div className="aspect-video w-full rounded-xl overflow-hidden bg-black border border-white/10 shadow-inner">
            <iframe
              className="w-full h-full"
              src="https://www.youtube.com/embed/oTahLEX3NXo?autoplay=1"
              title="Reference Style: What is Notion?"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
          <p className="text-xs text-slate-400 text-center pt-1">
            Official Notion product explainer showcasing the modular block architecture, cursor collaboration, and fluid pacing benchmark.
          </p>
        </div>
      )}

      {/* Spec Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-xs text-slate-300">
        <div className="flex items-center gap-3">
          <span className="text-slate-400">SPECS:</span>
          <span className="font-mono text-blue-400">1080P • 30 FPS</span>
          <span>•</span>
          <span className="font-mono text-emerald-400">H.264 MP4</span>
          <span>•</span>
          <span className="font-mono text-purple-400">AAC 192K AUDIO</span>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span>STYLE:</span>
          <span className="text-white font-medium">Modular Blocks &amp; Multi-Cursor Flow</span>
        </div>
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
