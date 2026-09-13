"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useReadingPassage, useSubmitReadingAttempt } from "@/hooks/use-reading";
import type { ReadingAttemptResult } from "@/types/api";

export function ReadingCard() {
  const { data: passage, isLoading, refetch } = useReadingPassage();
  const submit = useSubmitReadingAttempt();
  const [selected, setSelected] = React.useState<number | null>(null);
  const [result, setResult] = React.useState<ReadingAttemptResult | null>(null);

  React.useEffect(() => {
    setSelected(null);
    setResult(null);
  }, [passage?.id]);

  if (isLoading || !passage) {
    return <p className="text-sm text-muted-foreground">Loading a passage…</p>;
  }

  const onSubmit = () => {
    if (selected === null) return;
    submit.mutate(
      { passage_id: passage.id, selected_option_index: selected },
      { onSuccess: (data) => setResult(data) }
    );
  };

  const onNext = () => {
    setSelected(null);
    setResult(null);
    refetch();
  };

  return (
    <div className="flex flex-col gap-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {passage.cefr_level}
      </p>
      <p className="whitespace-pre-line text-sm leading-relaxed">{passage.passage_text}</p>
      <p className="text-base font-medium">{passage.question}</p>

      <div className="flex flex-col gap-2">
        {passage.options.map((option, index) => {
          const isSelected = selected === index;
          const isCorrectAnswer = result && index === result.correct_option_index;
          const isWrongSelection = result && isSelected && !result.is_correct;
          return (
            <button
              key={option}
              disabled={!!result}
              onClick={() => setSelected(index)}
              className={cn(
                "rounded-md border px-4 py-2.5 text-left text-sm transition-colors",
                !result && isSelected && "border-primary bg-[hsl(var(--primary)/0.1)]",
                !result && !isSelected && "border-input hover:bg-secondary",
                isCorrectAnswer && "border-[hsl(var(--good)/0.6)] bg-[hsl(var(--good)/0.12)]",
                isWrongSelection && "border-destructive bg-[hsl(var(--destructive)/0.1)]"
              )}
            >
              {option}
            </button>
          );
        })}
      </div>

      {!result ? (
        <Button onClick={onSubmit} disabled={selected === null || submit.isPending} className="w-fit">
          {submit.isPending ? "Checking…" : "Submit answer"}
        </Button>
      ) : (
        <div className="flex flex-col gap-3">
          <p className={cn("text-sm font-medium", result.is_correct ? "text-[hsl(var(--good))]" : "text-destructive")}>
            {result.is_correct ? "Correct!" : "Not quite."}
          </p>
          <p className="text-sm text-muted-foreground">{result.explanation}</p>
          <Button onClick={onNext} variant="outline" className="w-fit">
            Next passage
          </Button>
        </div>
      )}
    </div>
  );
}
