"use client";

import React, { useState } from "react";
import { CreateJobPayload } from "../lib/api";

interface JobFormProps {
  onSubmit: (payload: CreateJobPayload) => Promise<void>;
  isLoading: boolean;
}

export const JobForm: React.FC<JobFormProps> = ({ onSubmit, isLoading }) => {
  const [liveUrl, setLiveUrl] = useState("https://react.dev");
  const [repoUrl, setRepoUrl] = useState("https://github.com/facebook/react");
  const [mood, setMood] = useState("minimal");
  const [narration, setNarration] = useState(false);
  const [showRefDemo, setShowRefDemo] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const presets = [
    { name: "React", live: "https://react.dev", repo: "https://github.com/facebook/react" },
    { name: "Next.js", live: "https://nextjs.org", repo: "https://github.com/vercel/next.js" },
    { name: "FastAPI", live: "https://fastapi.tiangolo.com", repo: "https://github.com/fastapi/fastapi" },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;
    setError(null);
    try {
      await onSubmit({
        live_url: liveUrl,
        repo_url: repoUrl,
        mood,
        music: "default",
        narration,
      });
    } catch (err: any) {
      const msg = err.message || "Failed to create video job";
      if (msg === "Failed to fetch" || msg.includes("Failed to fetch")) {
        setError("Unable to connect to backend server. Make sure the FastAPI backend is running on http://127.0.0.1:8000 (run: python -m uvicorn api.main:app --port 8000).");
      } else {
        setError(msg);
      }
    }
  };

  return (
    <div className="w-full max-w-2xl space-y-4">
      {/* Reference Style Banner */}
      <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/20 border border-blue-500/30 rounded-2xl p-4 backdrop-blur-xl flex flex-col sm:flex-row items-center justify-between gap-3 shadow-lg shadow-blue-500/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold">
            ✦
          </div>
          <div>
            <div className="text-xs font-semibold text-blue-400 uppercase tracking-widest">
              NOTION-STYLE EXPLAINER ENGINE
            </div>
            <div className="text-sm text-slate-300 font-medium">
              Modular UI blocks, multi-user cursors &amp; fluid transitions
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setShowRefDemo(!showRefDemo)}
          className="px-3.5 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 text-xs font-medium transition flex items-center gap-1.5 whitespace-nowrap"
        >
          {showRefDemo ? "Hide Style Demo" : "▶ Watch Style Reference"}
        </button>
      </div>

      {/* Embedded Notion Reference Video Drawer */}
      {showRefDemo && (
        <div className="bg-[#0D0F14] border border-blue-500/30 rounded-2xl p-4 space-y-2 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
          <div className="flex items-center justify-between pb-2 border-b border-white/10 text-xs text-slate-400">
            <span className="font-semibold text-slate-200 uppercase tracking-wider">
              Style Benchmark: Notion Explainer Film (&quot;What is Notion?&quot;)
            </span>
            <span className="text-[11px] text-blue-400">Target Visual Flow</span>
          </div>
          <div className="aspect-video w-full rounded-xl overflow-hidden bg-black border border-white/10">
            <iframe
              className="w-full h-full"
              src="https://www.youtube.com/embed/oTahLEX3NXo?autoplay=1&mute=1"
              title="Style Reference: What is Notion?"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
          <p className="text-[11px] text-slate-400 pt-1 text-center">
            Your project will render in this exact aesthetic, replacing the content with your real working features from GitHub.
          </p>
        </div>
      )}

      {/* Main Submission Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-[#0D0F14]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl shadow-blue-500/5 space-y-6"
      >
        {/* Preset Selector */}
        <div className="flex items-center gap-2 pb-2 border-b border-white/10">
          <span className="text-xs uppercase font-semibold tracking-wider text-slate-400">
            Quick Try:
          </span>
          <div className="flex gap-2">
            {presets.map((p) => (
              <button
                key={p.name}
                type="button"
                onClick={() => {
                  setLiveUrl(p.live);
                  setRepoUrl(p.repo);
                }}
                className={`text-xs px-2.5 py-1 rounded-md border transition ${
                  repoUrl === p.repo
                    ? "bg-blue-600 text-white border-blue-500"
                    : "bg-white/5 text-slate-300 border-white/10 hover:bg-white/10"
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs uppercase font-semibold tracking-wider text-slate-400">
            Live Project URL
          </label>
          <input
            type="url"
            required
            value={liveUrl}
            onChange={(e) => setLiveUrl(e.target.value)}
            placeholder="https://mycoolapp.com"
            className="w-full bg-[#050505] border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition text-sm"
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs uppercase font-semibold tracking-wider text-slate-400">
            GitHub Repository URL
          </label>
          <input
            type="url"
            required
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            className="w-full bg-[#050505] border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition text-sm"
          />
          <p className="text-[11px] text-slate-500">
            Extracts real working features, architecture, and live routes directly from README &amp; AST.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs uppercase font-semibold tracking-wider text-slate-400">
              Soundtrack Mood
            </label>
            <select
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              className="w-full bg-[#050505] border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition text-sm"
            >
              <option value="minimal">Minimal Chill (100 BPM - Notion Style)</option>
              <option value="energetic">Energetic Pulse (128 BPM)</option>
              <option value="futuristic">Futuristic Electronic (140 BPM)</option>
            </select>
          </div>

          <div className="space-y-2 flex flex-col justify-end">
            <label className="flex items-center gap-3 cursor-pointer select-none bg-[#050505] border border-white/10 rounded-lg px-4 py-3">
              <input
                type="checkbox"
                checked={narration}
                onChange={(e) => setNarration(e.target.checked)}
                className="w-4 h-4 rounded text-blue-600 focus:ring-0 bg-transparent"
              />
              <span className="text-sm text-slate-300 font-medium">AI Voiceover</span>
            </label>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-headline text-2xl tracking-wide rounded-xl uppercase transition shadow-lg shadow-blue-600/30 disabled:opacity-50"
        >
          {isLoading ? "SYNTHESIZING LAUNCH FILM..." : "GENERATE NOTION-STYLE LAUNCH FILM"}
        </button>
      </form>
    </div>
  );
};
