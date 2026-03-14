"use client";

import { useState, useCallback } from "react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import ChatPane from "@/components/chat/ChatPane";
import ViewerPane from "@/components/viewer/ViewerPane";
import { generateProject, getProjectDownloadUrl } from "@/lib/api";
import type { Message, ProjectData, ERCResult } from "@/lib/types";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "system-init",
      type: "system",
      content:
        "PCB environment initialized. Describe your circuit in natural language, and I will generate a KiCad schematic and PCB layout for you.",
      timestamp: new Date(),
    },
  ]);

  const [projectData, setProjectData] = useState<ProjectData | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeView, setActiveView] = useState<"schematic" | "pcb">("schematic");

  const handleGenerate = useCallback(async (prompt: string) => {
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: "user",
      content: prompt,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsGenerating(true);

    const processingMessage: Message = {
      id: `ai-processing-${Date.now()}`,
      type: "ai",
      content: "Analyzing your request and generating circuit design...",
      timestamp: new Date(),
      isProcessing: true,
    };
    setMessages((prev) => [...prev, processingMessage]);

    try {
      const response = await generateProject(prompt, true);

      setMessages((prev) =>
        prev.filter((m) => m.id !== processingMessage.id)
      );

      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        type: "ai",
        content: formatAIResponse(response.erc_result),
        timestamp: new Date(),
        ercResult: response.erc_result,
      };
      setMessages((prev) => [...prev, aiMessage]);

      setProjectData({
        projectId: response.project_id,
        schematicUrl: response.schematic_url,
        pcbUrl: response.pcb_url,
        ercResult: response.erc_result,
        status: response.status,
      });
    } catch (error) {
      setMessages((prev) =>
        prev.filter((m) => m.id !== processingMessage.id)
      );

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: "ai",
        content: `Error generating design: ${
          error instanceof Error ? error.message : "Unknown error occurred"
        }`,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsGenerating(false);
    }
  }, []);

  const handleDownload = useCallback(() => {
    if (projectData?.projectId) {
      const downloadUrl = getProjectDownloadUrl(projectData.projectId);
      window.open(downloadUrl, "_blank");
    }
  }, [projectData]);

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Header
        onDownload={handleDownload}
        canDownload={!!projectData?.projectId}
      />

      <main className="flex flex-1 overflow-hidden">
        <ChatPane
          messages={messages}
          onGenerate={handleGenerate}
          isGenerating={isGenerating}
        />

        <ViewerPane
          projectData={projectData}
          activeView={activeView}
          onViewChange={setActiveView}
          isGenerating={isGenerating}
        />
      </main>

      <Footer isGenerating={isGenerating} />
    </div>
  );
}

function formatAIResponse(ercResult: ERCResult | undefined): string {
  if (!ercResult) {
    return "Circuit design generated successfully. You can view the schematic and PCB layout on the right.";
  }

  if (ercResult.passed) {
    return `Circuit design generated successfully!\n\nERC Status: ✓ Passed\n${ercResult.summary}\n\nYou can view the schematic and PCB layout on the right, or download the files to continue in KiCad.`;
  }

  const errorList = ercResult.messages?.length
    ? ercResult.messages.map((m) => `• ${m}`).join("\n")
    : "";

  return `Circuit design generated with warnings.\n\nERC Status: ⚠ Issues Found\n${ercResult.summary}\n${errorList}\n\nYou may want to review the design or try regenerating with more specific requirements.`;
}
