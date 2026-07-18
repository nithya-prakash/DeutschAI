"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LockedInsights } from "@/components/dashboard/locked-insights";
import { LogSessionForm } from "@/components/dashboard/log-session-form";
import { StatTile } from "@/components/dashboard/stat-tile";
import { StreakHeatmap } from "@/components/dashboard/streak-heatmap";
import { MemoryList } from "@/components/memory/memory-list";
import { useDashboardSummary } from "@/hooks/use-dashboard";
import { useRecentMemories } from "@/hooks/use-memory";
import { useTopics } from "@/hooks/use-topics";
import { useVocabulary } from "@/hooks/use-vocabulary";

export default function DashboardPage() {
  const { data, isLoading, isError } = useDashboardSummary();
  const { data: vocabulary } = useVocabulary();
  const { data: topics } = useTopics();
  const { data: memories } = useRecentMemories();

  if (isLoading) {
    return <p className="text-muted-foreground">Loading your dashboard…</p>;
  }
  if (isError || !data) {
    return <p className="text-destructive">Couldn&apos;t load your dashboard. Try refreshing.</p>;
  }

  const vocabDueCount = vocabulary?.filter((item) => item.is_due).length ?? 0;
  const masteredTopicsCount = topics?.filter((t) => t.status === "mastered").length ?? 0;

  const memberSince = new Date(data.member_since).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
  });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Your dashboard</h1>
        <p className="text-sm text-muted-foreground">Member since {memberSince}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <StatTile
          label="Current streak"
          value={`${data.current_streak_days} d`}
          note={data.current_streak_days > 0 ? "Keep it going!" : "Log a session to start"}
        />
        <StatTile label="Longest streak" value={`${data.longest_streak_days} d`} note="Best run so far" />
        <StatTile label="CEFR level" value={data.cefr_level} note="Target: German" />
        <StatTile
          label="This week"
          value={`${data.weekly_study_minutes} min`}
          note={`${data.total_study_minutes} min all-time`}
        />
        <StatTile
          label="Vocab due"
          value={String(vocabDueCount)}
          note={`${vocabulary?.length ?? 0} words tracked`}
        />
        <StatTile
          label="Topics mastered"
          value={topics ? `${masteredTopicsCount} / ${topics.length}` : "—"}
          note="Grammar + everyday topics"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Log today&apos;s session</CardTitle>
          <CardDescription>Track a session to keep your streak alive.</CardDescription>
        </CardHeader>
        <CardContent>
          <LogSessionForm />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Study streak</CardTitle>
          <CardDescription>Last 12 weeks. Darker means more minutes studied that day.</CardDescription>
        </CardHeader>
        <CardContent>
          <StreakHeatmap days={data.last_12_weeks} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent mistakes</CardTitle>
          <CardDescription>
            Written by the Assessment Agent whenever a quiz answer is wrong.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <MemoryList memories={memories ?? []} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Coming to your dashboard</CardTitle>
          <CardDescription>
            These metrics need the Learning, Assessment, and ML engines from later phases — shown
            here honestly as locked rather than filled with placeholder numbers.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LockedInsights insights={data.locked_insights} />
        </CardContent>
      </Card>
    </div>
  );
}
