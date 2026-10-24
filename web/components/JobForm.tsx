"use client";

import React, { useState } from "react";
import { CreateJobPayload } from "../lib/api";

interface JobFormProps {
  onSubmit: (payload: CreateJobPayload) => Promise<void>;
  isLoading: boolean;
}

export const JobForm: React.FC<JobFormProps> = ({ onSubmit, isLoading }) => {
  const [liveUrl, setLiveUrl] = useState("https://example.com");
  const [repoUrl, setRepoUrl] = useState("https://github.com/facebook/react");
  const [mood, setMood] = useState("energetic");
  const [narration, setNarration] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      setError(err.message || "Failed to create video job");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-2xl bg-[#0D0F14]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl shadow-blue-500/5 space-y-6"
    >
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
          className="w-full bg-[#050505] border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
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
          className="w-full bg-[#050505] border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-xs uppercase font-semibold tracking-wider text-slate-400">
            Soundtrack Mood
          </label>
          <select
            value={mood}
            onChange={(e) => setMood(e.target.value)}
            className="w-full bg-[#050505] border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
          >
            <option value="energetic">Energetic (128 BPM)</option>
            <option value="minimal">Minimal (100 BPM)</option>
            <option value="futuristic">Futuristic (140 BPM)</option>
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
        {isLoading ? "LAUNCHING PIPELINE..." : "GENERATE LAUNCH FILM"}
      </button>
    </form>
  );
};
