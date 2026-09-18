#!/usr/bin/env python3
"""
Student Attendance Management System
====================================
A simple command-line application to manage student attendance.

Features
--------
1. Add a student      - register a new student with name and roll number
2. Mark attendance    - record Present/Absent for a student on a date
3. View records       - list students and their attendance summary
4. Exit

Data is stored in `students.json` (created automatically in the same
directory as this script).

How to run
----------
    python3 attendance_management.py

Requires Python 3.6+. No external packages needed.
"""

import json
import os
import sys
from datetime import date, datetime

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.json")

EMPTY_DB = {"students": {}, "attendance": {}}
# students   : {roll_no: {"name": str, "email": str, "created": "YYYY-MM-DD"}}
# attendance : {roll_no: {"YYYY-MM-DD": "P" | "A"}}


def load_db():
    """Load the database from disk; return an empty structure on first run."""
    if not os.path.exists(DATA_FILE):
        return {"students": {}, "attendance": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: could not read data file ({exc}). Starting fresh.")
        return {"students": {}, "attendance": {}}
    db.setdefault("students", {})
    db.setdefault("attendance", {})
    return db


def save_db(db):
    """Persist the database to disk."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def prompt_nonempty(message):
    """Ask until the user types something non-empty."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("  ! Value cannot be empty. Please try again.")


def prompt_date(message="Enter date (YYYY-MM-DD, blank for today): "):
    """Ask for a date; blank input means today. Re-asks on invalid input."""
    while True:
        raw = input(message).strip()
        if not raw:
            return date.today().isoformat()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("  ! Invalid date. Use the format YYYY-MM-DD (e.g. 2026-09-18).")


def prompt_status():
    """Ask for attendance status: P (present) or A (absent)."""
    while True:
        raw = input("Status - (P)resent or (A)bsent: ").strip().lower()
        if raw in ("p", "present"):
            return "P"
        if raw in ("a", "absent"):
            return "A"
        print("  ! Please enter P or A.")


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def add_student(db):
    print("\n--- Add Student ---")
    roll_no = prompt_nonempty("Roll number: ")
    if roll_no in db["students"]:
        print(f"! A student with roll number '{roll_no}' already exists "
              f"({db['students'][roll_no]['name']}).")
        return
    name = prompt_nonempty("Full name: ")
    email = input("Email (optional, press Enter to skip): ").strip()

    db["students"][roll_no] = {
        "name": name,
        "email": email,
        "created": date.today().isoformat(),
    }
    db["attendance"].setdefault(roll_no, {})
    save_db(db)
    print(f"OK: {name} (Roll no {roll_no}) added successfully.")


def mark_attendance(db):
    print("\n--- Mark Attendance ---")
    if not db["students"]:
        print("! No students yet. Add a student first (option 1).")
        return
    roll_no = prompt_nonempty("Roll number: ")
    if roll_no not in db["students"]:
        print(f"! No student found with roll number '{roll_no}'.")
        return
    day = prompt_date()
    status = prompt_status()

    previous = db["attendance"].get(roll_no, {}).get(day)
    db["attendance"].setdefault(roll_no, {})[day] = status
    save_db(db)

    name = db["students"][roll_no]["name"]
    label = "Present" if status == "P" else "Absent"
    if previous:
        prev_label = "Present" if previous == "P" else "Absent"
        print(f"Updated: {name} on {day} changed from {prev_label} to {label}.")
    else:
        print(f"Recorded: {name} marked {label} on {day}.")


def view_records(db):
    print("\n--- Attendance Records ---")
    if not db["students"]:
        print("! No students yet. Add a student first (option 1).")
        return

    today = date.today().isoformat()
    total_width = 78
    print("-" * total_width)
    print(f"{'Roll':<10}{'Name':<22}{'Present':<9}{'Absent':<8}{'Total':<7}"
          f"{'%':<7}{'Today':<10}")
    print("-" * total_width)

    for roll_no, info in db["students"].items():
        records = db["attendance"].get(roll_no, {})
        present = sum(1 for v in records.values() if v == "P")
        absent = sum(1 for v in records.values() if v == "A")
        total = present + absent
        pct = f"{(present / total * 100):.0f}%" if total else "-"
        today_status = {"P": "Present", "A": "Absent"}.get(records.get(today), "-")
        print(f"{roll_no:<10}{info['name'][:20]:<22}{present:<9}{absent:<8}"
              f"{total:<7}{pct:<7}{today_status:<10}")
    print("-" * total_width)

    show_detail = input("Show full day-by-day history for a student? (y/N): ").strip().lower()
    if show_detail in ("y", "yes"):
        roll_no = prompt_nonempty("Roll number: ")
        if roll_no not in db["students"]:
            print(f"! No student found with roll number '{roll_no}'.")
            return
        records = db["attendance"].get(roll_no, {})
        name = db["students"][roll_no]["name"]
        if not records:
            print(f"No attendance recorded yet for {name}.")
            return
        print(f"\nHistory for {name} (Roll no {roll_no}):")
        for day in sorted(records):
            label = "Present" if records[day] == "P" else "Absent"
            print(f"  {day}  {label}")


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

MENU = """
=========================================
  Student Attendance Management System
=========================================
1. Add student
2. Mark attendance
3. View records
4. Exit
"""

ACTIONS = {
    "1": add_student,
    "2": mark_attendance,
    "3": view_records,
}


def main():
    db = load_db()
    while True:
        print(MENU)
        choice = input("Choose an option (1-4): ").strip()
        if choice == "4":
            print("Goodbye! Attendance data saved to", DATA_FILE)
            break
        action = ACTIONS.get(choice)
        if action:
            action(db)
        else:
            print("! Invalid choice. Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted - data saved. Goodbye!")
        sys.exit(0)
