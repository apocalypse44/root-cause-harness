import type { Service, Incident, IncidentCreate, Report } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, init);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  services: {
    list: () => fetcher<Service[]>("/api/services"),
  },
  incidents: {
    list: (serviceId?: string) =>
      fetcher<Incident[]>(`/api/incidents${serviceId ? `?service_id=${serviceId}` : ""}`),
    get: (id: string) => fetcher<Incident>(`/api/incidents/${id}`),
    create: (body: IncidentCreate) =>
      fetcher<Incident>("/api/incidents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
  },
  investigations: {
    getReport: (incidentId: string) =>
      fetcher<Report>(`/api/investigations/${incidentId}/report`),
    async *investigate(incidentId: string) {
      const res = await fetch(`${API}/api/investigations/${incidentId}/investigate`, {
        method: "POST",
      });
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          const dataMatch = line.match(/data: (.+)/);
          if (dataMatch) {
            yield JSON.parse(dataMatch[1]);
          }
        }
      }
    },
  },
};
