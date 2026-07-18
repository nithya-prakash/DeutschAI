"""Progress forecasting: projects when a learner will finish mastering the
curriculum, by fitting a simple linear trend to their mastery history over
time. Deliberately not a heavier model — with only a handful of mastery
dates per user, a hand-rolled least-squares fit is exactly as much model as
the data supports; anything fancier would be overfitting noise.
"""
from dataclasses import dataclass
from datetime import date, timedelta

# Fewer than this many distinct mastery dates isn't enough to fit a trend
# line from — one point can't have a slope.
MIN_DISTINCT_DATES = 2


@dataclass
class MilestoneForecast:
    topics_remaining: int
    projected_date: date


def predict_milestone(
    progress_points: list[tuple[date, int]], total_topics: int
) -> MilestoneForecast | None:
    """`progress_points`: (date, cumulative topics mastered as of that date),
    sorted ascending, one entry per date a mastery status changed. Returns
    `None` if there's too little history to fit a trend, the trend isn't
    actually progressing, or the curriculum is already fully mastered."""
    distinct_dates = {d for d, _count in progress_points}
    if len(distinct_dates) < MIN_DISTINCT_DATES:
        return None

    last_date, last_count = progress_points[-1]
    topics_remaining = total_topics - last_count
    if topics_remaining <= 0:
        return None

    x0 = progress_points[0][0]
    xs = [(d - x0).days for d, _count in progress_points]
    ys = [count for _d, count in progress_points]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0:
        return None
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True)) / denominator

    if slope <= 0:
        # Flat or regressing trend — no honest forecast to extrapolate.
        return None

    days_remaining = topics_remaining / slope
    projected_date = last_date + timedelta(days=round(days_remaining))
    return MilestoneForecast(topics_remaining=topics_remaining, projected_date=projected_date)
