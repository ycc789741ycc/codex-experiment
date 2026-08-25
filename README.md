# Book Recall App (Forgetting Curve Scheduler)

This app helps you review a finished book at spaced intervals inspired by the forgetting curve.

## What it does
- You provide a book title and the date you finished reading.
- The app creates future review dates using this interval plan (days after finishing):
  `1, 3, 7, 14, 30, 60, 120, 240`
- It exports an `.ics` calendar file you can import into Google Calendar, Apple Calendar, Outlook, etc.

## Usage

```bash
python book_recall_app.py "Atomic Habits" --finished-on 2026-03-09 --output-dir ./out --hour 9
```

Example output:

```text
Created review reminder file: out/atomic-habits-review-plan.ics
Upcoming review dates:
  1. 2026-03-10
  2. 2026-03-12
  ...
```

## Calendar reminders
After generating the `.ics` file:
1. Open your calendar app.
2. Import the generated file.
3. Enable notification/reminder rules if your calendar requires it.

## Run tests

```bash
pytest -q
```
