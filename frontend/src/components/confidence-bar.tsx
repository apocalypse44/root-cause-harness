export function ConfidenceBar({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  const color = pct >= 80 ? "bg-green-500" : pct >= 50 ? "bg-yellow-500" : "bg-red-500";

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-1000`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-mono font-bold">{pct}%</span>
    </div>
  );
}
