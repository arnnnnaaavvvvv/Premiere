"use client";

import React, { useEffect, useState } from "react";
import { JobForm } from "../components/JobForm";
import { ProgressStepper } from "../components/ProgressStepper";
import { VideoPlayer } from "../components/VideoPlayer";
import { CreateJobPayload, JobStatusResponse, fetchJobStatus, submitJob } from "../lib/api";

export default function Home() {
  const [currentJob, setCurrentJob] = useState<JobStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Poll for job status updates when an active job is processing
  useEffect(() => {
    let isMounted = true;
    if (!currentJob || currentJob.status === "done" || currentJob.status === "failed") {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await fetchJobStatus(currentJob.id);
        if (isMounted) {
          setCurrentJob(updated);
        }
      } catch (err) {
        if (isMounted) {
          console.error("Error polling job status:", err);
        }
      }
    }, 2000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [currentJob]);

  const handleJobSubmit = async (payload: CreateJobPayload) => {
    setIsLoading(true);
    try {
      const job = await submitJob(payload);
      setCurrentJob(job);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16 relative overflow-hidden bg-[#050505]">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-blue-600/10 blur-[140px] pointer-events-none" />

      {/* Hero Header */}
      <div className="text-center space-y-4 mb-12 z-10 max-w-3xl">
        <div className="inline-block px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold uppercase tracking-widest text-blue-400">
          NOTION-STYLE PRODUCT EXPLAINER ENGINE
        </div>
        <h1 className="text-6xl sm:text-8xl font-headline tracking-tight text-white uppercase leading-none">
          CRAFT THE FILM. <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-blue-500 to-indigo-500">
            LAUNCH IN MINUTES.
          </span>
        </h1>
        <p className="text-slate-400 text-lg sm:text-xl font-normal max-w-xl mx-auto">
          Paste any live URL and GitHub repository. Premiere distills your project&apos;s real working features and produces a broadcast-quality Notion-style product demo film.
        </p>
      </div>

      {/* Main Interactive Stage */}
      <div className="w-full flex justify-center z-10">
        {!currentJob && (
          <JobForm onSubmit={handleJobSubmit} isLoading={isLoading} />
        )}

        {currentJob && currentJob.status !== "done" && (
          <ProgressStepper job={currentJob} />
        )}

        {currentJob && currentJob.status === "done" && (
          <VideoPlayer
            jobId={currentJob.id}
            videoUrl={currentJob.video_url}
            onReset={() => setCurrentJob(null)}
          />
        )}
      </div>

      {/* Footer Info */}
      <footer className="mt-20 text-center text-xs text-slate-600 uppercase tracking-widest z-10">
        Bebas Neue Display • 60 FPS Capture • Librosa Beat Sync • Remotion Engine
      </footer>
    </main>
  );
}
