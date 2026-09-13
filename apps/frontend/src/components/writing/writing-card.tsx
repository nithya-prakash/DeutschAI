"use client";

import * as React from "react";
import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useSubmitWriting, useWritingPrompt } from "@/hooks/use-writing";
import { ApiRequestError } from "@/lib/api-client";
import type { WritingSubmissionResult } from "@/types/api";

export function WritingCard() {
  const { data: prompt, isLoading, refetch } = useWritingPrompt();
  const submit = useSubmitWriting();
  const [text, setText] = React.useState("");
  const [result, setResult] = React.useState<WritingSubmissionResult | null>(null);
  const [notConfigured, setNotConfigured] = React.useState(false);

  React.useEffect(() => {
    setText("");
    setResult(null);
    setNotConfigured(false);
  }, [prompt?.id]);

  if (isLoading || !prompt) {
    return <p className="text-sm text-muted-foreground">Loading a prompt…</p>;
  }

  const onSubmit = () => {
    if (!text.trim()) return;
    setNotConfigured(false);
    submit.mutate(
      { prompt_id: prompt.id, submitted_text: text.trim() },
      {
        onSuccess: (data) => setResult(data),
        onError: (err) => {
          if (err instanceof ApiRequestError && err.status === 503) {
            setNotConfigured(true);
          }
        },
      }
    );
  };

  const onNext = () => {
    setText("");
    setResult(null);
    refetch();
  };

  return (
    <div className="flex flex-col gap-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {prompt.cefr_level}
      </p>
      <p className="text-base font-medium">{prompt.prompt_text}</p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={!!result}
        placeholder="Schreib deine Antwort auf Deutsch…"
        rows={6}
        className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
      />

      {notConfigured && (
        <Card className="border-[hsl(var(--activity-listening)/0.4)]">
          <CardContent className="flex items-start gap-3 p-4">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--activity-listening))]" />
            <div>
              <p className="text-sm font-medium">Writing grading isn&apos;t configured yet</p>
              <p className="text-sm text-muted-foreground">
                This needs an <code>ANTHROPIC_API_KEY</code> set on the backend to grade
                submissions. Everything else in the app works without it.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {!result ? (
        <Button onClick={onSubmit} disabled={!text.trim() || submit.isPending} className="w-fit">
          {submit.isPending ? "Grading…" : "Submit"}
        </Button>
      ) : (
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap gap-4 text-sm">
            {result.grammar_score !== null && <span>Grammar: {result.grammar_score}/100</span>}
            {result.vocabulary_score !== null && <span>Vocabulary: {result.vocabulary_score}/100</span>}
            {result.task_completion_score !== null && (
              <span>Task completion: {result.task_completion_score}/100</span>
            )}
          </div>
          {result.feedback && <p className="text-sm text-muted-foreground">{result.feedback}</p>}
          <Button onClick={onNext} variant="outline" className="w-fit">
            Next prompt
          </Button>
        </div>
      )}
    </div>
  );
}
