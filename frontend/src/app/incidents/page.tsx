"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { IncidentsTable } from "@/components/incidents-table";
import { CreateIncidentDialog } from "@/components/create-incident-dialog";

function IncidentsContent() {
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

export default function IncidentsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <IncidentsContent />
    </Suspense>
  );
}
