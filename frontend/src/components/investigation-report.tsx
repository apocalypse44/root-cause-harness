"use client";

import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ConfidenceBar } from "./confidence-bar";
import { Timeline } from "./timeline";
import { EvidenceSection } from "./evidence-section";
import { api } from "@/lib/api";
import type { Report } from "@/lib/types";

type AgentStatus = { name: string; status: "pending" | "running" | "done"; summary?: string };

export function InvestigationReport({ incidentId }: { incidentId: string }) {
  const [investigating, setInvestigating] = useState(false);
  const [agents, setAgents] = useState<AgentStatus[]>([
    { name: "deployment", status: "pending" },
    { name: "logs", status: "pending" },
    { name: "metrics", status: "pending" },
    { name: "git", status: "pending" },
    { name: "correlation", status: "pending" },
  ]);
  const [report, setReport] = useState<Report | null>(null);

  const { data: incident } = useQuery({
    queryKey: ["incident", incidentId],
    queryFn: () => api.incidents.get(incidentId),
  });

  const { data: existingReport } = useQuery({
    queryKey: ["report", incidentId],
    queryFn: () => api.investigations.getReport(incidentId),
    enabled: incident?.has_report === true,
    retry: false,
  });

  const startInvestigation = useCallback(async () => {
    setInvestigating(true);
    try {
      for await (const event of api.investigations.investigate(incidentId)) {
        if (event.event === "agent_start") {
          setAgents((prev) =>
            prev.map((a) => (a.name === event.agent ? { ...a, status: "running" } : a))
          );
        } else if (event.event === "agent_complete") {
          setAgents((prev) =>
            prev.map((a) => (a.name === event.agent ? { ...a, status: "done", summary: event.summary } : a))
          );
        } else if (event.event === "complete") {
          setReport(event.report);
        }
      }
    } finally {
      setInvestigating(false);
    }
  }, [incidentId]);

  const displayReport = report || existingReport;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">{incident?.title || "Loading..."}</h2>
        <div className="flex gap-2 mt-2">
          {incident && (
            <>
              <Badge variant="outline">{incident.service_name}</Badge>
              <Badge variant="outline">{incident.severity}</Badge>
              <Badge>{incident.status}</Badge>
            </>
          )}
        </div>
      </div>

      {!displayReport && !investigating && (
        <Button size="lg" onClick={startInvestigation}>
          Start Investigation
        </Button>
      )}

      {investigating && (
        <Card>
          <CardHeader><CardTitle>Investigation in Progress</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {agents.map((a) => (
              <div key={a.name} className="flex items-center gap-3 text-sm">
                <span className={`h-2 w-2 rounded-full ${
                  a.status === "done" ? "bg-green-500" : a.status === "running" ? "bg-yellow-500 animate-pulse" : "bg-muted"
                }`} />
                <span className="capitalize font-medium w-24">{a.name}</span>
                <span className="text-muted-foreground text-xs">{a.summary || (a.status === "running" ? "Analyzing..." : "")}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {displayReport && (
        <>
          <Separator />

          <Card>
            <CardHeader><CardTitle>Root Cause</CardTitle></CardHeader>
            <CardContent>
              <p className="text-lg mb-4">{displayReport.root_cause}</p>
              <ConfidenceBar confidence={displayReport.confidence} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Timeline</CardTitle></CardHeader>
            <CardContent>
              <Timeline events={displayReport.evidence?.timeline || []} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Evidence</CardTitle></CardHeader>
            <CardContent>
              <EvidenceSection findings={displayReport.evidence?.agent_findings || []} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Recommendations</CardTitle></CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-1">
                {displayReport.recommendations?.map((r, i) => (
                  <li key={i} className="text-sm">{r}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
