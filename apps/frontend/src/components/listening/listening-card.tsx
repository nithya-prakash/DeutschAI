"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useListeningScript, useScriptAudioUrl, useSubmitListeningAttempt } from "@/hooks/use-listening";
import type { ListeningAttemptResult } from "@/types/api";

export function ListeningCard() {
  const { data: script, isLoading, refetch } = useListeningScript();
  const audioUrl = useScriptAudioUrl(script?.id ?? null);
  const submit = useSubmitListeningAttempt();
  const [selected, setSelected] = React.useState<number | null>(null);
  const [result, setResult] = React.useState<ListeningAttemptResult | null>(null);

  React.useEffect(() => {
    setSelected(null);
    setResult(null);
  }, [script?.id]);

  if (isLoading || !script) {
    return <p className="text-sm text-muted-foreground">Loading a clip…</p>;
  }

  const onSubmit = () => {
    if (selected === null) return;
    submit.mutate(
      { script_id: script.id, selected_option_index: selected },
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
        {script.cefr_level}
      </p>
      {audioUrl ? (
        // eslint-disable-next-line jsx-a11y/media-has-caption -- synthesized German speech, no transcript exposed by design
        <audio controls src={audioUrl} className="w-full" />
      ) : (
        <p className="text-sm text-muted-foreground">Loading audio…</p>
      )}
      <p className="text-base font-medium">{script.question}</p>

      <div className="flex flex-col gap-2">
        {script.options.map((option, index) => {
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
            Next clip
          </Button>
        </div>
      )}
    </div>
  );
}
