"use client";

import { useState, useCallback } from "react";
import { generateProject, getProject } from "@/lib/api";
import type { ProjectData, ERCResult, GenerateResponse } from "@/lib/types";

interface UseProjectReturn {
  projectData: ProjectData | null;
  isLoading: boolean;
  error: string | null;
  generate: (prompt: string, runErc?: boolean) => Promise<GenerateResponse | null>;
  loadProject: (projectId: string) => Promise<void>;
  clearProject: () => void;
}

export function useProject(): UseProjectReturn {
  const [projectData, setProjectData] = useState<ProjectData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = useCallback(
    async (prompt: string, runErc = true): Promise<GenerateResponse | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await generateProject(prompt, runErc);

        setProjectData({
          projectId: response.project_id,
          schematicUrl: response.schematic_url,
          pcbUrl: response.pcb_url,
          ercResult: response.erc_result,
          status: response.status,
        });

        return response;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to generate project";
        setError(message);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const loadProject = useCallback(async (projectId: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getProject(projectId);

      setProjectData({
        projectId: response.project_id,
        schematicUrl: response.schematic_url,
        pcbUrl: response.pcb_url,
        ercResult: response.erc_result,
        status: response.status,
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load project";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearProject = useCallback(() => {
    setProjectData(null);
    setError(null);
  }, []);

  return {
    projectData,
    isLoading,
    error,
    generate,
    loadProject,
    clearProject,
  };
}
