"use client";

import * as React from "react";
import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ChatMessage } from "@/components/tutor/chat-message";
import { useAskTutor, useConversation, useConversations } from "@/hooks/use-tutor";
import { ApiRequestError } from "@/lib/api-client";
import { cn } from "@/lib/utils";

export default function TutorPage() {
  const [activeConversationId, setActiveConversationId] = React.useState<string | null>(null);
  const [question, setQuestion] = React.useState("");
  const [notConfigured, setNotConfigured] = React.useState(false);

  const { data: conversations } = useConversations();
  const { data: activeConversation } = useConversation(activeConversationId);
  const ask = useAskTutor();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setNotConfigured(false);
    ask.mutate(
      { question: question.trim(), conversation_id: activeConversationId ?? undefined },
      {
        onSuccess: (data) => {
          setActiveConversationId(data.conversation_id);
          setQuestion("");
        },
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
        <h1 className="text-2xl font-semibold">Ask the Tutor Agent</h1>
        <p className="text-sm text-muted-foreground">
          Answers are grounded in the app&apos;s own A1 grammar notes via retrieval-augmented
          generation, tailored to your CEFR level.
        </p>
      </div>

      {notConfigured && (
        <Card className="border-[hsl(var(--activity-listening)/0.4)]">
          <CardContent className="flex items-start gap-3 p-5">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--activity-listening))]" />
            <div>
              <p className="text-sm font-medium">Tutor Agent isn&apos;t configured yet</p>
              <p className="text-sm text-muted-foreground">
                This needs an <code>ANTHROPIC_API_KEY</code> set on the backend to generate
                real, grounded answers. Everything else in the app works without it — see
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
                {c.last_message_preview ?? "New conversation"}
              </button>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardDescription>
            {activeConversation ? `${activeConversation.messages.length} messages` : "Ask anything about German grammar or vocabulary."}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex min-h-[120px] flex-col gap-3">
            {activeConversation?.messages.map((m) => <ChatMessage key={m.id} message={m} />)}
            {!activeConversation && (
              <p className="text-sm text-muted-foreground">No messages yet.</p>
            )}
          </div>

          <form onSubmit={onSubmit} className="flex gap-2">
            <Input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. When do I use kein instead of nicht?"
              className="flex-1"
            />
            <Button type="submit" disabled={ask.isPending}>
              {ask.isPending ? "Asking…" : "Ask"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
