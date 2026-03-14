import type { GenerateResponse, ProjectResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function toFullUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${API_BASE}${path.startsWith("/") ? "" : "/"}${path}`;
}

export async function generateProject(
  prompt: string,
  runErc = true
): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
      run_erc: runErc,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Generation failed with status ${response.status}`
    );
  }

  const data = await response.json();
  
  return {
    ...data,
    schematic_url: toFullUrl(data.schematic_url),
    pcb_url: toFullUrl(data.pcb_url),
  };
}

export async function getProject(projectId: string): Promise<ProjectResponse> {
  const response = await fetch(`${API_BASE}/projects/${projectId}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Project not found");
    }
    throw new Error(`Failed to fetch project: ${response.status}`);
  }

  const data = await response.json();
  
  return {
    ...data,
    schematic_url: toFullUrl(data.schematic_url),
    pcb_url: toFullUrl(data.pcb_url),
  };
}

export function getProjectDownloadUrl(projectId: string): string {
  return `${API_BASE}/projects/${projectId}/download`;
}

export function getFileUrl(projectId: string, filename: string): string {
  return `${API_BASE}/files/${projectId}/${filename}`;
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
