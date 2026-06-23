"use client";

import { useSearchParams } from "next/navigation";
import { IncidentsTable } from "@/components/incidents-table";
import { CreateIncidentDialog } from "@/components/create-incident-dialog";

export default function IncidentsPage() {
  const params = useSearchParams();
  const serviceId = params.get("service_id") || undefined;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Incidents</h2>
        <CreateIncidentDialog />
      </div>
      <IncidentsTable serviceId={serviceId} />
    </div>
  );
}
