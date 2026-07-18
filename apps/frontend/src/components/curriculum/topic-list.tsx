"use client";

import { cn } from "@/lib/utils";
import { useUpdateTopicProgress } from "@/hooks/use-topics";
import type { TopicRead, TopicStatus } from "@/types/api";

const NEXT_STATUS: Record<TopicStatus, TopicStatus> = {
  not_started: "in_progress",
  in_progress: "mastered",
  mastered: "not_started",
};

const STATUS_LABEL: Record<TopicStatus, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  mastered: "Mastered",
};

function StatusPill({ status }: { status: TopicStatus }) {
  return (
    <span
      className={cn(
        "inline-flex w-24 shrink-0 justify-center rounded-full px-2 py-0.5 text-xs font-medium transition-colors",
        status === "not_started" && "bg-secondary text-muted-foreground",
        status === "in_progress" && "bg-[hsl(var(--primary)/0.15)] text-primary",
        status === "mastered" && "bg-primary text-primary-foreground"
      )}
    >
      {STATUS_LABEL[status]}
    </span>
  );
}

export function TopicList({ title, topics }: { title: string; topics: TopicRead[] }) {
  const updateProgress = useUpdateTopicProgress();
  const masteredCount = topics.filter((t) => t.status === "mastered").length;
  const pct = topics.length ? Math.round((masteredCount / topics.length) * 100) : 0;

  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between">
        <h3 className="text-sm font-semibold">{title}</h3>
        <span className="text-xs text-muted-foreground">
          {masteredCount} / {topics.length} mastered ({pct}%)
        </span>
      </div>
      <div className="mb-3 h-2 overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <ul className="flex flex-col gap-1.5">
        {topics.map((topic) => (
          <li key={topic.id} className="flex items-center justify-between gap-3 border-b border-border py-1.5 last:border-none">
            <span
              className={cn(
                "text-sm",
                topic.status === "mastered" && "text-muted-foreground line-through"
              )}
            >
              {topic.name}
            </span>
            <button
              type="button"
              onClick={() =>
                updateProgress.mutate({ id: topic.id, status: NEXT_STATUS[topic.status] })
              }
              disabled={updateProgress.isPending}
              title="Click to advance status"
            >
              <StatusPill status={topic.status} />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
