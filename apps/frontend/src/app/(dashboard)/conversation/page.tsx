"use client";

import * as React from "react";
import { AlertTriangle } from "lucide-react";

import { LockedInsights } from "@/components/dashboard/locked-insights";
import { Recorder } from "@/components/conversation/recorder";
import { TurnCard } from "@/components/conversation/turn-card";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  useSpeechConversation,
  useSpeechConversations,
  useSubmitTurn,
} from "@/hooks/use-conversation-mode";
import { ApiRequestError } from "@/lib/api-client";
import { cn } from "@/lib/utils";

export default function ConversationPage() {
  const [activeConversationId, setActiveConversationId] = React.useState<string | null>(null);
  const [notConfigured, setNotConfigured] = React.useState(false);

  const { data: conversations } = useSpeechConversations();
  const { data: activeConversation } = useSpeechConversation(activeConversationId);
  const submitTurn = useSubmitTurn();

  const onRecorded = (audio: Blob) => {
    setNotConfigured(false);
    submitTurn.mutate(
      { audio, conversationId: activeConversationId },
      {
        onSuccess: (data) => setActiveConversationId(data.conversation_id),
        onError: (err) => {
          if (err instanceof ApiRequestError && err.status === 503) {
            setNotConfigured(true);
          }
        },
      }
    );
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Conversation Mode</h1>
        <p className="text-sm text-muted-foreground">
          Practice spoken German with an AI conversation partner. Speak a reply, and get it
          transcribed, answered, and scored for grammar and vocabulary.
        </p>
      </div>

      {notConfigured && (
        <Card className="border-[hsl(var(--activity-listening)/0.4)]">
          <CardContent className="flex items-start gap-3 p-5">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--activity-listening))]" />
            <div>
              <p className="text-sm font-medium">Conversation Agent isn&apos;t configured yet</p>
              <p className="text-sm text-muted-foreground">
                This needs an <code>ANTHROPIC_API_KEY</code> set on the backend to generate real
                replies and scoring. Everything else in the app works without it — see
                docs/ROADMAP.md.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {conversations && conversations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Past conversations</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-1.5">
            <button
              className={cn(
                "rounded-md px-3 py-1.5 text-left text-sm hover:bg-secondary",
                activeConversationId === null && "bg-secondary"
              )}
              onClick={() => setActiveConversationId(null)}
            >
              + New conversation
            </button>
            {conversations.map((c) => (
              <button
                key={c.id}
                className={cn(
                  "truncate rounded-md px-3 py-1.5 text-left text-sm hover:bg-secondary",
                  activeConversationId === c.id && "bg-secondary"
                )}
                onClick={() => setActiveConversationId(c.id)}
              >
                {c.last_turn_preview ?? "New conversation"}
              </button>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardDescription>
            {activeConversation
              ? `${activeConversation.turns.length} turns`
              : "Tap the mic and say something in German to start."}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex min-h-[120px] flex-col gap-3">
            {activeConversation?.turns.map((t) => <TurnCard key={t.id} turn={t} />)}
            {!activeConversation && (
              <p className="text-sm text-muted-foreground">No turns yet.</p>
            )}
          </div>

          <div className="flex justify-center border-t border-border pt-4">
            <Recorder onRecorded={onRecorded} disabled={submitTurn.isPending} />
          </div>
          {submitTurn.isPending && (
            <p className="text-center text-xs text-muted-foreground">
              Transcribing, generating a reply, and scoring…
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Coming soon</CardTitle>
        </CardHeader>
        <CardContent>
          <LockedInsights insights={["Pronunciation scoring", "Fluency scoring"]} />
        </CardContent>
      </Card>
    </div>
  );
}
