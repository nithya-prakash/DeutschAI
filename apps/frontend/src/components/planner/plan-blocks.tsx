import { cn } from "@/lib/utils";
import type { PlanBlock } from "@/types/api";

const ACTIVITY_LABEL: Record<string, string> = {
  vocab: "Vocab review",
  grammar: "Grammar",
  listening: "Listening",
  speaking: "Speaking",
};

const ACTIVITY_VAR: Record<string, string> = {
  vocab: "--activity-vocab",
  grammar: "--activity-grammar",
  listening: "--activity-listening",
  speaking: "--activity-speaking",
};

export function PlanBlocks({ blocks }: { blocks: PlanBlock[] }) {
  const total = blocks.reduce((sum, b) => sum + b.minutes, 0);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex h-3 overflow-hidden rounded-full bg-secondary">
        {blocks.map((block) => (
          <div
            key={block.activity}
            style={{
              width: `${total ? (block.minutes / total) * 100 : 0}%`,
              backgroundColor: `hsl(var(${ACTIVITY_VAR[block.activity] ?? "--primary"}))`,
            }}
            title={`${ACTIVITY_LABEL[block.activity] ?? block.activity}: ${block.minutes} min`}
          />
        ))}
      </div>

      <ul className="flex flex-col gap-2">
        {blocks.map((block) => (
          <li key={block.activity} className="flex items-center gap-3 rounded-md border border-border p-3">
            <span
              className={cn("h-2.5 w-2.5 shrink-0 rounded-full")}
              style={{ backgroundColor: `hsl(var(${ACTIVITY_VAR[block.activity] ?? "--primary"}))` }}
            />
            <div className="flex-1">
              <p className="text-sm font-medium">{ACTIVITY_LABEL[block.activity] ?? block.activity}</p>
              <p className="text-xs text-muted-foreground">{block.reason}</p>
            </div>
            <span className="text-sm font-semibold text-muted-foreground">{block.minutes} min</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
