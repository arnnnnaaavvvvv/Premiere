"use client";

import React from "react";
import { JobStatusResponse } from "../lib/api";

const STAGES = [
  { key: "analyzing", label: "Analyze Codebase" },
  { key: "scripting", label: "Script Director" },
  { key: "capturing", label: "Browser Capture" },
  { key: "rendering", label: "Notion 1080p Render" },
];

export const ProgressStepper: React.FC<{ job: JobStatusResponse }> = ({ job }) => {
  const getStageIndex = (status: string) => {
    if (status === "analyzing") return 0;
    if (status === "scripting") return 1;
    if (status === "capturing") return 2;
    if (status === "rendering") return 3;
    if (status === "done") return 4;
    return -1;
  };

  const currentIndex = getStageIndex(job.status);

  return (
    <div className="w-full max-w-2xl bg-[#0D0F14]/90 border border-white/10 rounded-2xl p-8 backdrop-blur-xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs uppercase font-semibold tracking-widest text-blue-400">
            AUTONOMOUS PIPELINE
          </span>
          <h3 className="text-2xl font-headline text-white mt-1 uppercase">
            {job.current_stage || "Processing"}
          </h3>
        </div>
        <div className="text-4xl font-headline text-white">
          {job.progress}%
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 transition-all duration-500 rounded-full shadow-lg shadow-blue-500/50"
          style={{ width: `${job.progress}%` }}
        />
      </div>

      {/* Step Indicators */}
      <div className="grid grid-cols-4 gap-2 pt-2">
        {STAGES.map((s, idx) => {
          const isDone = currentIndex > idx || job.status === "done";
          const isCurrent = currentIndex === idx;
          return (
            <div key={s.key} className="text-center space-y-1">
              <div
                className={`w-3 h-3 mx-auto rounded-full transition-colors ${
                  isDone
                    ? "bg-blue-500 shadow-sm shadow-blue-500"
                    : isCurrent
                    ? "bg-blue-400 animate-ping"
                    : "bg-white/10"
                }`}
              />
              <span
                className={`text-[11px] uppercase tracking-wider block ${
                  isDone || isCurrent ? "text-slate-200 font-medium" : "text-slate-500"
                }`}
              >
                {s.label}
              </span>
            </div>
          );
        })}
      </div>

      {job.error_message && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg">
          {job.error_message}
        </div>
      )}
    </div>
  );
};
