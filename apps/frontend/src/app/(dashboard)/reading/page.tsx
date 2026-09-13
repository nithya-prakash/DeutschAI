"use client";

import { Card, CardContent } from "@/components/ui/card";
import { ReadingCard } from "@/components/reading/reading-card";

export default function ReadingPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Reading comprehension</h1>
        <p className="text-sm text-muted-foreground">
          Read a short passage and answer one question about it — graded deterministically, no
          LLM needed. A wrong answer is recorded as a mistake you can review later.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <ReadingCard />
        </CardContent>
      </Card>
    </div>
  );
}
