import type { RecommendationResult } from "@/types/api";

export function RecommendedFocus({ recommendations }: { recommendations: RecommendationResult }) {
  const { vocab, topics } = recommendations;

  if (vocab.length === 0 && topics.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Nothing to recommend yet — review some vocabulary and take a quiz or two, and
        personalized suggestions will show up here.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      {vocab.length > 0 && (
        <div>
          <p className="mb-2 text-sm font-medium text-muted-foreground">Vocabulary to review</p>
          <ul className="flex flex-col gap-2">
            {vocab.map((v) => (
              <li key={v.id} className="rounded-md border border-border px-3 py-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{v.german}</span>
                  <span className="text-xs text-muted-foreground">{v.english}</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{v.reason}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
      {topics.length > 0 && (
        <div>
          <p className="mb-2 text-sm font-medium text-muted-foreground">Topics to focus on</p>
          <ul className="flex flex-col gap-2">
            {topics.map((t) => (
              <li key={t.topic_id} className="rounded-md border border-border px-3 py-2 text-sm">
                <p className="font-medium">{t.topic_name}</p>
                <p className="mt-1 text-xs text-muted-foreground">{t.reason}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
