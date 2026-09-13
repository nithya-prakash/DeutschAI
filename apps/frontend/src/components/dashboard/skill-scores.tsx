import type { SkillScores as SkillScoresType } from "@/types/api";

const LABELS: Record<keyof SkillScoresType, string> = {
  grammar: "Grammar",
  vocabulary: "Vocabulary",
  speaking: "Speaking",
  reading: "Reading",
  listening: "Listening",
  writing: "Writing",
};

export function SkillScores({ scores }: { scores: SkillScoresType }) {
  const entries = Object.entries(scores) as [keyof SkillScoresType, number | null][];

  return (
    <div className="flex flex-col gap-3">
      {entries.map(([key, value]) => (
        <div key={key} className="flex flex-col gap-1">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">{LABELS[key]}</span>
            <span className="text-muted-foreground">
              {value === null ? "Not enough data yet" : `${Math.round(value)}/100`}
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
            {value !== null && (
              <div
                className="h-full rounded-full bg-primary"
                style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
              />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
