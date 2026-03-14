export interface ERCResult {
  passed: boolean;
  messages: string[];
  summary: string;
}

export interface GenerateRequest {
  prompt: string;
  run_erc?: boolean;
}

export interface GenerateResponse {
  project_id: string;
  schematic_url: string;
  pcb_url: string;
  erc_result: ERCResult;
  status: string;
}

export interface ProjectResponse {
  project_id: string;
  prompt: string;
  schematic_url: string;
  pcb_url: string;
  erc_result: ERCResult;
  status: string;
  created_at: string;
}

export interface ProjectData {
  projectId: string;
  schematicUrl: string;
  pcbUrl: string;
  ercResult?: ERCResult;
  status: string;
}

export interface Message {
  id: string;
  type: "system" | "user" | "ai";
  content: string;
  timestamp: Date;
  ercResult?: ERCResult;
  isProcessing?: boolean;
  isError?: boolean;
}
