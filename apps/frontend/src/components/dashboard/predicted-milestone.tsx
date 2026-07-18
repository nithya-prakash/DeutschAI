import type { PredictedMilestone as PredictedMilestoneType } from "@/types/api";

export function PredictedMilestone({
  milestone,
}: {
  milestone: PredictedMilestoneType | null;
}) {
  if (!milestone) {
    return (
      <p className="text-sm text-muted-foreground">
        Not enough mastery history yet to project a finish date — master a few more topics and
        this will fill in.
      </p>
    );
  }

  const projected = new Date(milestone.projected_date).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <p className="text-sm">
      At your current pace, you&apos;ll master the remaining{" "}
      <span className="font-semibold">{milestone.topics_remaining}</span> topic
      {milestone.topics_remaining === 1 ? "" : "s"} by{" "}
      <span className="font-semibold">{projected}</span>.
    </p>
  );
}
