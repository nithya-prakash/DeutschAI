import type { MemoryRead } from "@/types/api";

const MEMORY_TYPE_LABEL: Record<string, string> = {
  mistake: "Mistake",
  forgotten_word: "Forgotten word",
  pronunciation_issue: "Pronunciation",
  note: "Note",
};

export function MemoryList({ memories }: { memories: MemoryRead[] }) {
  if (memories.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No mistakes recorded yet — they show up here after a quiz you get wrong.
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {memories.map((memory) => (
        <li key={memory.id} className="rounded-md border border-border p-3">
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-muted-foreground">
              {MEMORY_TYPE_LABEL[memory.memory_type] ?? memory.memory_type}
            </span>
            {memory.related_topic_name && (
              <span className="text-xs text-muted-foreground">{memory.related_topic_name}</span>
            )}
          </div>
          <p className="text-sm">{memory.content}</p>
        </li>
      ))}
    </ul>
  );
}
