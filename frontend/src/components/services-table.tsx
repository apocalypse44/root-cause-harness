"use client";

import { useQuery } from "@tanstack/react-query";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import type { Service } from "@/lib/types";

const statusColor: Record<string, string> = {
  healthy: "bg-green-500",
  degraded: "bg-yellow-500",
  down: "bg-red-500",
};

export function ServicesTable() {
  const { data: services, isLoading } = useQuery({
    queryKey: ["services"],
    queryFn: api.services.list,
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Service</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Deployments</TableHead>
          <TableHead>Incidents</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {services?.map((s: Service) => (
          <TableRow key={s.id}>
            <TableCell className="font-medium">{s.name}</TableCell>
            <TableCell>
              <Badge variant="outline" className="gap-1.5">
                <span className={`h-2 w-2 rounded-full ${statusColor[s.status]}`} />
                {s.status}
              </Badge>
            </TableCell>
            <TableCell>{s.deployment_count}</TableCell>
            <TableCell>
              <a href={`/incidents?service_id=${s.id}`} className="underline">
                {s.incident_count}
              </a>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
