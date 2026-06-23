"use client";

import { useQuery } from "@tanstack/react-query";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { Incident } from "@/lib/types";

const severityColor: Record<string, string> = {
  low: "bg-blue-500",
  medium: "bg-yellow-500",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

const statusVariant: Record<string, "default" | "secondary" | "outline"> = {
  open: "default",
  investigating: "secondary",
  resolved: "outline",
};

export function IncidentsTable({ serviceId }: { serviceId?: string }) {
  const { data: incidents, isLoading } = useQuery({
    queryKey: ["incidents", serviceId],
    queryFn: () => api.incidents.list(serviceId),
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Service</TableHead>
          <TableHead>Severity</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Created</TableHead>
          <TableHead></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {incidents?.map((inc: Incident) => (
          <TableRow key={inc.id}>
            <TableCell className="font-medium max-w-xs truncate">{inc.title}</TableCell>
            <TableCell>{inc.service_name}</TableCell>
            <TableCell>
              <Badge variant="outline" className="gap-1.5">
                <span className={`h-2 w-2 rounded-full ${severityColor[inc.severity]}`} />
                {inc.severity}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge variant={statusVariant[inc.status]}>{inc.status}</Badge>
            </TableCell>
            <TableCell>{new Date(inc.created_at).toLocaleString()}</TableCell>
            <TableCell>
              <Button variant="outline" size="sm" render={<a href={`/incidents/${inc.id}/report`} />}>
                {inc.has_report ? "View Report" : "Investigate"}
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
