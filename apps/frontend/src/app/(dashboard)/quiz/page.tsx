"use client";

import * as React from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { QuizCard } from "@/components/quiz/quiz-card";
import { useTopics } from "@/hooks/use-topics";
import { cn } from "@/lib/utils";

export default function QuizPage() {
  const { data: topics, isLoading } = useTopics();
  const [selectedTopicId, setSelectedTopicId] = React.useState<string | null>(null);

  const grammarTopics = topics?.filter((t) => t.category === "grammar") ?? [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Practice quiz</h1>
        <p className="text-sm text-muted-foreground">
          The Assessment Agent grades multiple-choice answers deterministically — no LLM needed.
          A wrong answer is recorded as a mistake you can review later.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Pick a grammar topic</CardTitle>
          <CardDescription>One question per topic for now.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Loading topics…</p>}
          <div className="flex flex-wrap gap-2">
            {grammarTopics.map((topic) => (
              <button
                key={topic.id}
                onClick={() => setSelectedTopicId(topic.id)}
                className={cn(
                  "rounded-full border px-3 py-1.5 text-sm transition-colors",
                  selectedTopicId === topic.id
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-input hover:bg-secondary"
                )}
              >
                {topic.name}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {selectedTopicId && (
        <Card>
          <CardContent className="pt-6">
            <QuizCard topicId={selectedTopicId} onNext={() => setSelectedTopicId(null)} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
