"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { TopicList } from "@/components/curriculum/topic-list";
import { useTopics } from "@/hooks/use-topics";

export default function CurriculumPage() {
  const { data, isLoading, isError } = useTopics();

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">A1 → A2 curriculum roadmap</h1>
        <p className="text-sm text-muted-foreground">
          Click a topic&apos;s status to cycle: not started → in progress → mastered.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Your progress</CardTitle>
          <CardDescription>
            Matches the Goethe-Zertifikat A1 grammar syllabus and Sprechen topic list.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
          {isError && <p className="text-sm text-destructive">Couldn&apos;t load the curriculum.</p>}
          {data && (
            <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
              <TopicList
                title="Grammar foundations"
                topics={data.filter((t) => t.category === "grammar")}
              />
              <TopicList
                title="Everyday topics (Sprechen)"
                topics={data.filter((t) => t.category === "everyday_topic")}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
