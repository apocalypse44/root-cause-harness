"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface AgentFinding {
  agent_name: string;
  summary: string;
  data: Record<string, unknown>[];
}

export function EvidenceSection({ findings }: { findings: AgentFinding[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-3">
      {findings.map((f) => (
        <Card key={f.agent_name} className="cursor-pointer" onClick={() => setExpanded(expanded === f.agent_name ? null : f.agent_name)}>
          <CardHeader className="py-3">
            <CardTitle className="text-sm flex items-center justify-between">
              <span className="capitalize">{f.agent_name} Agent</span>
              <span className="text-xs text-muted-foreground">{expanded === f.agent_name ? "▼" : "▶"}</span>
            </CardTitle>
            <p className="text-xs text-muted-foreground">{f.summary}</p>
          </CardHeader>
          {expanded === f.agent_name && (
            <CardContent>
              <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-64">
                {JSON.stringify(f.data, null, 2)}
              </pre>
            </CardContent>
          )}
        </Card>
      ))}
    </div>
  );
}
