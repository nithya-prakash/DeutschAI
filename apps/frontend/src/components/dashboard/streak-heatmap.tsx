"use client";

import * as React from "react";

import type { DailyMinutes } from "@/types/api";

export function heatLevel(minutes: number): number {
  if (minutes <= 0) return 0;
  if (minutes <= 15) return 1;
  if (minutes <= 30) return 2;
  if (minutes <= 45) return 3;
  if (minutes <= 60) return 4;
  return 5;
}

export function StreakHeatmap({ days }: { days: DailyMinutes[] }) {
  return (
    <div>
      <div className="overflow-x-auto pb-1">
        <div
          className="grid w-max gap-[3px]"
          style={{ gridTemplateRows: "repeat(7, 14px)", gridAutoFlow: "column" }}
        >
          {days.map((d) => {
            const level = heatLevel(d.minutes);
            return (
              <div
                key={d.date}
                title={`${d.date} — ${d.minutes ? `${d.minutes} min` : "no session"}`}
                className="h-[14px] w-[14px] rounded-[3px]"
                style={{ backgroundColor: `hsl(var(--heat-${level}))` }}
              />
            );
          })}
        </div>
      </div>
      <div className="mt-3 flex items-center gap-1.5 text-xs text-muted-foreground">
        <span>Less</span>
        {[0, 1, 2, 3, 4, 5].map((level) => (
          <div
            key={level}
            className="h-[14px] w-[14px] rounded-[3px]"
            style={{ backgroundColor: `hsl(var(--heat-${level}))` }}
          />
        ))}
        <span>More</span>
      </div>
    </div>
  );
}
