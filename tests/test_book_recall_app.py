from datetime import date
from pathlib import Path

import pytest

from book_recall_app import ForgettingCurveScheduler, build_output_path, create_ics


def test_scheduler_uses_default_intervals():
    scheduler = ForgettingCurveScheduler()

    plan = scheduler.build_plan("Deep Work", date(2026, 3, 9))

    assert plan.review_dates[0].isoformat() == "2026-03-10"
    assert plan.review_dates[1].isoformat() == "2026-03-12"
    assert plan.review_dates[-1].isoformat() == "2026-11-04"


def test_scheduler_rejects_explicit_empty_intervals():
    with pytest.raises(
        ValueError, match="interval_days must include at least one interval"
    ):
        ForgettingCurveScheduler([])


def test_ics_contains_events_for_each_review_date():
    scheduler = ForgettingCurveScheduler([1, 7])
    plan = scheduler.build_plan("Atomic Habits", date(2026, 1, 1))

    ics = create_ics(plan, reminder_hour=8)

    assert "BEGIN:VCALENDAR" in ics
    assert ics.count("BEGIN:VEVENT") == 2
    assert "SUMMARY:Review book - Atomic Habits" in ics
    assert "DTSTART:20260102T080000" in ics
    assert "DTSTART:20260108T080000" in ics


def test_build_output_path_sanitizes_title():
    output_path = build_output_path("Clean Code (2nd Ed.)", output_dir=Path("/tmp"))

    assert str(output_path).endswith("clean-code--2nd-ed-review-plan.ics")
