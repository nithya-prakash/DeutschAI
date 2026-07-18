import { describe, expect, it } from "vitest";

import { heatLevel } from "@/components/dashboard/streak-heatmap";

describe("heatLevel", () => {
  it("maps zero/negative minutes to level 0", () => {
    expect(heatLevel(0)).toBe(0);
    expect(heatLevel(-5)).toBe(0);
  });

  it("buckets minutes into 6 levels", () => {
    expect(heatLevel(10)).toBe(1);
    expect(heatLevel(25)).toBe(2);
    expect(heatLevel(40)).toBe(3);
    expect(heatLevel(55)).toBe(4);
    expect(heatLevel(90)).toBe(5);
  });

  it("is monotonically non-decreasing", () => {
    const levels = [0, 10, 20, 30, 40, 50, 60, 70, 90].map(heatLevel);
    for (let i = 1; i < levels.length; i++) {
      const previous = levels[i - 1] ?? 0;
      const current = levels[i] ?? 0;
      expect(current).toBeGreaterThanOrEqual(previous);
    }
  });
});
