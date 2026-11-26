from datetime import date, timedelta
import json

FILENAME = "user_data.json"


class Habit:
    def __init__(self, name: str, completed_dates=None):
        self._name = name
        self.set_name(name)

        if completed_dates is None:
            self._completed_dates = []

        else:
            self._completed_dates = list(completed_dates)

    def check_in(self, date_str=None):
        if date_str is None:
            date_str = date.today().isoformat()
        return date_str

    def get_name(self):
        return self._name

    def set_name(self, name):
        if not name or not name.strip():
            raise ValueError("Habit name cannot be empty.")
        self._name = name.strip()

    def get_completed_dates(self):
        return self._completed_dates

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "name": self._name,
            "completed_dates": self._completed_dates
        }


class DailyHabit(Habit):

    def check_in(self, date_str=None):
        date_str = super().check_in(date_str)

        if date_str in self._completed_dates:
            return False
        self._completed_dates.append(date_str)
        return True

    def get_streak(self):
        check_date = date.today()

        if check_date.isoformat() not in self._completed_dates:
            check_date -= timedelta(days=1)

        streak = 0

        while check_date.isoformat() in self._completed_dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak

    def get_status(self):
        today = date.today().isoformat()

        if today in self._completed_dates:
            status = "Done today"

        else:
            status = "Not done today"

        streak = self.get_streak()

        return f"[Daily] {self._name} - {status} (Streak: {streak})"

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            completed_dates=data.get("completed_dates", [])
        )


class WeeklyHabit(Habit):
    def __init__(self, name, target_per_week: int = 3, completed_dates=None):
        super().__init__(name, completed_dates)
        self.set_target_per_week(target_per_week)

    def get_target_per_week(self):
        return self._target_per_week

    def set_target_per_week(self, target):
        if target < 1:
            raise ValueError("Goal per week must be atleast 1")
        self._target_per_week = target

    def check_in(self, date_str=None):
        date_str = super().check_in(date_str)
        self._completed_dates.append(date_str)
        return True

    def get_status(self):
        current_week = date.today().isocalendar()[:2]
        count = 0

        for dates in self._completed_dates:
            if date.fromisoformat(dates).isocalendar()[:2] == current_week:
                count += 1

        return f"[Weekly] {self._name} - {count}/{self._target_per_week} this week"

    def to_dict(self):
        data = super().to_dict()
        data["target_per_week"] = self._target_per_week
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            target_per_week=data.get("target_per_week", 3),
            completed_dates=data.get("completed_dates", [])
        )


class LimitHabit(Habit):
    def __init__(self, name, daily_limit: int = 2, completed_dates=None):
        super().__init__(name, completed_dates)
        self.set_daily_limit(daily_limit)

    def set_daily_limit(self, limit):
        if limit < 0:
            raise ValueError("Invalid! Limit must be 0 or higher")
        self._daily_limit = limit

    def get_daily_limit(self):
        return self._daily_limit

    def check_in(self, date_str=None):
        date_str = super().check_in(date_str)
        self._completed_dates.append(date_str)

        if self._completed_dates.count(date_str) <= self._daily_limit:
            return True
        else:
            return False

    def get_status(self):
        today = date.today().isoformat()
        count = self._completed_dates.count(today)
        return f"[Limit] {self._name} - {count}/{self._daily_limit} today"

    def to_dict(self):
        data = super().to_dict()
        data["daily_limit"] = self._daily_limit
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            daily_limit=data.get("daily_limit", 2),
            completed_dates=data.get("completed_dates", [])
        )


class MoodLog:
    def __init__(self, score: int, note: str = "", date_str: str = None):
        self._date = date_str if date_str else date.today().isoformat()
        self.set_score(score)
        self._note = note.strip()

    def get_date(self):
        return self._date

    def get_score(self):
        return self._score

    def get_note(self):
        return self._note

    def set_score(self, score):
        if not (1 <= score <= 5):
            raise ValueError("A mood score must be between 1 and 5")
        self._score = score

    def get_status(self):
        mood_comp = f"[{self._date}] Mood: {self._score}/5"
        if self._note:
            mood_comp += f" - {self._note}"
        return mood_comp

    def to_dict(self):
        return {
            "date": self._date,
            "score": self._score,
            "note": self._note
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            score=data["score"],
            note=data.get("note", ""),
            date_str=data.get("date")
        )


class HabitManager:
    def __init__(self, filename=FILENAME):
        self._filename = filename
        self._habits = []
        self._moodlogs = []
        self.load_data()

    def save_data(self):
        data = {
            "habits": [h.to_dict() for h in self._habits],
            "moodlogs": [m.to_dict() for m in self._moodlogs]
        }
        with open(self._filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def load_data(self):
        try:
            with open(self._filename, "r", encoding="utf-8") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            self._habits = []
            self._moodlogs = []
            return

        self._habits = []
        for item in data.get("habits", []):
            habit_type = item.get("type")
            if habit_type == "DailyHabit":
                self._habits.append(DailyHabit.from_dict(item))

            elif habit_type == "WeeklyHabit":
                self._habits.append(WeeklyHabit.from_dict(item))

            elif habit_type == "LimitHabit":
                self._habits.append(LimitHabit.from_dict(item))

        self._moodlogs = [MoodLog.from_dict(m)
                          for m in data.get("moodlogs", [])]

    def add_habit(self, habit):
