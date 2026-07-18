"use client";

import { Button } from "@/components/ui/button";
import { useDeleteWord, useReviewWord } from "@/hooks/use-vocabulary";
import { REVIEW_QUALITY, type VocabularyItemRead } from "@/types/api";

export function VocabTable({ items }: { items: VocabularyItemRead[] }) {
  const review = useReviewWord();
  const remove = useDeleteWord();

  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">No words yet — add your first one above.</p>;
  }

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
          <th className="py-2 pr-2 font-medium">German</th>
          <th className="py-2 pr-2 font-medium">English</th>
          <th className="py-2 pr-2 font-medium">Example</th>
          <th className="py-2 pr-2 font-medium">Due</th>
          <th className="py-2 pr-2 font-medium">Actions</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id} className="border-b border-border last:border-none">
            <td className="py-2 pr-2 font-medium">{item.german}</td>
            <td className="py-2 pr-2">{item.english}</td>
            <td className="py-2 pr-2 text-muted-foreground">{item.example_sentence ?? "—"}</td>
            <td className="py-2 pr-2">
              {item.is_due ? (
                <span className="rounded-full bg-[hsl(var(--activity-listening)/0.15)] px-2 py-0.5 text-xs font-semibold text-[hsl(var(--activity-listening))]">
                  Due
                </span>
              ) : (
                <span className="text-xs text-muted-foreground">{item.next_review_date}</span>
              )}
            </td>
            <td className="py-2 pr-2">
              <div className="flex flex-wrap gap-1.5">
                {item.is_due && (
                  <>
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={review.isPending}
                      onClick={() => review.mutate({ id: item.id, quality: REVIEW_QUALITY.again })}
                    >
                      Again
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={review.isPending}
                      onClick={() => review.mutate({ id: item.id, quality: REVIEW_QUALITY.hard })}
                    >
                      Hard
                    </Button>
                    <Button
                      size="sm"
                      disabled={review.isPending}
                      onClick={() => review.mutate({ id: item.id, quality: REVIEW_QUALITY.good })}
                    >
                      Good
                    </Button>
                    <Button
                      size="sm"
                      disabled={review.isPending}
                      onClick={() => review.mutate({ id: item.id, quality: REVIEW_QUALITY.easy })}
                    >
                      Easy
                    </Button>
                  </>
                )}
                <Button
                  size="sm"
                  variant="ghost"
                  aria-label={`Remove ${item.german}`}
                  disabled={remove.isPending}
                  onClick={() => remove.mutate(item.id)}
                >
                  ✕
                </Button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
