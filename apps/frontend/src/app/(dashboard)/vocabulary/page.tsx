"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AddWordForm } from "@/components/vocabulary/add-word-form";
import { VocabTable } from "@/components/vocabulary/vocab-table";
import { useVocabulary } from "@/hooks/use-vocabulary";

export default function VocabularyPage() {
  const { data, isLoading, isError } = useVocabulary();

  const dueCount = data?.filter((item) => item.is_due).length ?? 0;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Vocabulary notebook</h1>
        <p className="text-sm text-muted-foreground">
          Spaced repetition (SM-2) — words you struggle with come back sooner, words you know well
          come back later.
          {dueCount > 0 && ` ${dueCount} due today.`}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add a word</CardTitle>
          <CardDescription>German, English, and an optional example sentence.</CardDescription>
        </CardHeader>
        <CardContent>
          <AddWordForm />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Your words</CardTitle>
          <CardDescription>Sorted by next review date.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
          {isError && <p className="text-sm text-destructive">Couldn&apos;t load your vocabulary.</p>}
          {data && <VocabTable items={data} />}
        </CardContent>
      </Card>
    </div>
  );
}
