import { Lock } from "lucide-react";

export function LockedInsights({ insights }: { insights: string[] }) {
  return (
    <ul className="flex flex-col gap-2">
      {insights.map((insight) => (
        <li
          key={insight}
          className="flex items-center gap-2.5 rounded-md border border-dashed border-border px-3 py-2 text-sm text-muted-foreground"
        >
          <Lock className="h-3.5 w-3.5 shrink-0" />
          {insight}
        </li>
      ))}
    </ul>
  );
}
