import { InvestigationReport } from "@/components/investigation-report";

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <InvestigationReport incidentId={id} />;
}
