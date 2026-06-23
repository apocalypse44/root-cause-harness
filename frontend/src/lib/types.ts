export type ServiceStatus = "healthy" | "degraded" | "down";
export type Severity = "low" | "medium" | "high" | "critical";
export type IncidentStatus = "open" | "investigating" | "resolved";

export interface Service {
  id: string;
  name: string;
  status: ServiceStatus;
  created_at: string;
  deployment_count: number;
  incident_count: number;
}

export interface Incident {
  id: string;
  service_id: string;
  service_name: string;
  title: string;
  severity: Severity;
  status: IncidentStatus;
  created_at: string;
  has_report: boolean;
}

export interface IncidentCreate {
  service_id: string;
  title: string;
  severity: Severity;
}

export interface Report {
  id: string;
  incident_id: string;
  root_cause: string;
  confidence: number;
  evidence: {
    timeline: { time: string; event: string }[];
    agent_findings: {
      agent_name: string;
      summary: string;
      data: Record<string, unknown>[];
    }[];
  };
  recommendations: string[];
  generated_at: string;
}

export interface InvestigationEvent {
  event: string;
  agent?: string;
  summary?: string;
  report?: Report;
}
