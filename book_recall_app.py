from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable, List
from uuid import uuid4


DEFAULT_INTERVAL_DAYS = [1, 3, 7, 14, 30, 60, 120, 240]


@dataclass(frozen=True)
class ReviewPlan:
    book_title: str
    finished_on: date
    review_dates: List[date]


class ForgettingCurveScheduler:
    """Create spaced review dates that follow a practical forgetting-curve pattern."""

    def __init__(self, interval_days: Iterable[int] | None = None) -> None:
        intervals = list(DEFAULT_INTERVAL_DAYS if interval_days is None else interval_days)
        if not intervals:
            raise ValueError("interval_days must include at least one interval")
        if any(day <= 0 for day in intervals):
            raise ValueError("all intervals must be positive")
        self.interval_days = intervals

    def build_plan(self, book_title: str, finished_on: date) -> ReviewPlan:
        review_dates = [finished_on + timedelta(days=day) for day in self.interval_days]
        return ReviewPlan(book_title=book_title, finished_on=finished_on, review_dates=review_dates)


def create_ics(plan: ReviewPlan, reminder_hour: int = 9) -> str:
    """Create iCalendar content for all review dates in the plan."""
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Book Recall App//EN",
        "CALSCALE:GREGORIAN",
    ]

    for review_date in plan.review_dates:
        start_dt = datetime.combine(review_date, time(hour=reminder_hour))
        end_dt = start_dt + timedelta(minutes=30)
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uuid4()}@book-recall-app",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:Review book - {plan.book_title}",
                (
                    f"DESCRIPTION:Spaced repetition reminder for '{plan.book_title}'. "
                    f"Originally finished on {plan.finished_on.isoformat()}."
                ),
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\n".join(lines) + "\n"


def build_output_path(book_title: str, output_dir: Path) -> Path:
    safe_name = "".join(ch if ch.isalnum() else "-" for ch in book_title.lower()).strip("-")
    safe_name = safe_name or "book"
    return output_dir / f"{safe_name}-review-plan.ics"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate forgetting-curve calendar reminders for book reviews."
    )
    parser.add_argument("title", help="Book title")
    parser.add_argument(
        "--finished-on",
        default=date.today().isoformat(),
        help="Date you finished reading (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where the generated .ics file should be saved.",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=9,
        help="Reminder hour in 24h format, default: 9",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    finished_on = date.fromisoformat(args.finished_on)

    scheduler = ForgettingCurveScheduler()
    plan = scheduler.build_plan(args.title, finished_on)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = build_output_path(args.title, output_dir)

    ics_content = create_ics(plan, reminder_hour=args.hour)
    output_path.write_text(ics_content, encoding="utf-8")

    print(f"Created review reminder file: {output_path}")
    print("Upcoming review dates:")
    for idx, review_date in enumerate(plan.review_dates, start=1):
        print(f"  {idx}. {review_date.isoformat()}")


if __name__ == "__main__":
    main()
