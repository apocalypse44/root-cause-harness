interface TimelineEvent {
  time: string;
  event: string;
}

export function Timeline({ events }: { events: TimelineEvent[] }) {
  return (
    <div className="space-y-3">
      {events.map((e, i) => (
        <div key={i} className="flex gap-3">
          <div className="flex flex-col items-center">
            <div className="h-3 w-3 rounded-full bg-primary mt-1" />
            {i < events.length - 1 && <div className="w-px flex-1 bg-border" />}
          </div>
          <div className="pb-4">
            <p className="text-xs text-muted-foreground font-mono">{e.time}</p>
            <p className="text-sm">{e.event}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
