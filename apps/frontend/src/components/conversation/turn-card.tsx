"use client";

import { useTurnAudioUrl } from "@/hooks/use-conversation-mode";
import { cn } from "@/lib/utils";
import type { SpeechTurnRead } from "@/types/api";

export function TurnCard({ turn }: { turn: SpeechTurnRead }) {
  const isUser = turn.role === "user";
  const audioUrl = useTurnAudioUrl(turn.id);

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "flex max-w-[80%] flex-col gap-2 rounded-lg px-4 py-2.5 text-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-foreground"
        )}
      >
        <p>{turn.text}</p>
        {audioUrl && <audio controls src={audioUrl} className="h-8 w-56" />}
        {isUser && (turn.grammar_score !== null || turn.vocabulary_score !== null) && (
          <div className="flex flex-col gap-1 rounded-md bg-background/20 px-2.5 py-2 text-xs">
            <div className="flex gap-4">
              {turn.grammar_score !== null && <span>Grammar: {turn.grammar_score}/100</span>}
              {turn.vocabulary_score !== null && (
                <span>Vocabulary: {turn.vocabulary_score}/100</span>
              )}
            </div>
            {turn.feedback && <p className="opacity-90">{turn.feedback}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
