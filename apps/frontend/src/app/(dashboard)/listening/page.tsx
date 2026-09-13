"use client";

import { Card, CardContent } from "@/components/ui/card";
import { ListeningCard } from "@/components/listening/listening-card";

export default function ListeningPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Listening comprehension</h1>
        <p className="text-sm text-muted-foreground">
          Listen to a short locally-synthesized clip and answer one question about it — graded
          deterministically, no LLM needed. A wrong answer is recorded as a mistake you can
          review later.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <ListeningCard />
        </CardContent>
      </Card>
    </div>
  );
}
