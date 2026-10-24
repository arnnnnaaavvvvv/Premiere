const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface CreateJobPayload {
  live_url: string;
  repo_url: string;
  mood: string;
  music: string;
  narration: boolean;
}

export interface JobStatusResponse {
  id: string;
  live_url: string;
  repo_url: string;
  mood: string;
  status: "queued" | "analyzing" | "scripting" | "capturing" | "rendering" | "done" | "failed";
  progress: number;
  current_stage: string;
  error_message?: string | null;
  video_url?: string | null;
}

export async function submitJob(payload: CreateJobPayload): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE}/api/v1/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: "Failed to submit job" }));
    throw new Error(errData.detail || "Error initiating video pipeline");
  }

  return res.json();
}

export async function fetchJobStatus(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE}/api/v1/jobs/${jobId}`);
  if (!res.ok) {
    throw new Error("Failed to fetch job status");
  }
  return res.json();
}

export function getVideoDownloadUrl(jobId: string): string {
  return `${API_BASE}/api/v1/jobs/${jobId}/video`;
}
