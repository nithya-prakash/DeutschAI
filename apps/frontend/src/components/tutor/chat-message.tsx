import { cn } from "@/lib/utils";
import type { MessageRead } from "@/types/api";

export function ChatMessage({ message }: { message: MessageRead }) {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2.5 text-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-foreground"
        )}
      >
        {message.content}
      </div>
    </div>
  );
}
