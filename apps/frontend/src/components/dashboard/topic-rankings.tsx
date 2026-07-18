import type { TopicRanking } from "@/types/api";

function RankingList({ topics, emptyText }: { topics: TopicRanking[]; emptyText: string }) {
  if (topics.length === 0) {
    return <p className="text-sm text-muted-foreground">{emptyText}</p>;
  }
  return (
    <ul className="flex flex-col gap-2">
      {topics.map((t) => (
        <li
          key={t.topic_id}
          className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
        >
          <span>{t.topic_name}</span>
          <span className="text-xs text-muted-foreground">
            {t.mistake_count} mistake{t.mistake_count === 1 ? "" : "s"}
            {t.accuracy !== null ? ` · ${Math.round(t.accuracy)}% accuracy` : ""}
          </span>
        </li>
      ))}
    </ul>
  );
}

export function TopicRankings({
  weakest,
  strongest,
}: {
  weakest: TopicRanking[];
  strongest: TopicRanking[];
}) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <p className="mb-2 text-sm font-medium text-muted-foreground">Needs work</p>
        <RankingList topics={weakest} emptyText="No weak spots recorded yet." />
      </div>
      <div>
        <p className="mb-2 text-sm font-medium text-muted-foreground">Strongest</p>
        <RankingList topics={strongest} emptyText="Answer some quizzes to see your strengths." />
      </div>
    </div>
  );
}
