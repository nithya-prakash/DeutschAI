"use client";

import { Card, CardContent } from "@/components/ui/card";
import { WritingCard } from "@/components/writing/writing-card";

export default function WritingPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Writing practice</h1>
        <p className="text-sm text-muted-foreground">
          Respond to a short prompt in German — the Writing Agent grades grammar, vocabulary, and
          task completion via Claude, and gives brief feedback. Requires{" "}
          <code>ANTHROPIC_API_KEY</code>.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <WritingCard />
        </CardContent>
      </Card>
    </div>
  );
}
