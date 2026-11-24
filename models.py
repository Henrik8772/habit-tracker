from datetime import date, timedelta
import json

FILENAME = "user_habit.json"

class Habit:
    def __init__(self, name:str, completed_dates = None):
        self._name = name

        if completed_dates is None:
            self._completed_dates = []

        else:
            self._completed_dates = list(completed_dates)

    def check_in(self, date_str = None):
        if date_str is None:
            self.date_str = date.today().isoformat()
        return date_str

class DailyHabit(Habit):
    def __init__(self, name, completed_dates=None):
        super().__init__(name, completed_dates)

    def check_in(self, date_str = None):
        self.date_str = super().check_in(date_str)

        if date_str in self._completed_dates:
            return False
        self._completed_dates.append(date_str)
        return True

    def get_streak(self):
        self.check_date = date.today()

        if self.check_date.isoformat() not in self._completed_dates:
            self.check_date -= timedelta(days=1)

        streak = 0

        while self.check_date.isoformat() in self._completed_dates:
            streak += 1
            self.check_date -= timedelta(days=1)

        return streak

    def get_status(self):
        
        
        

class HabitManager:

    def save_habit_data(habits: list):
        with open(FILENAME, "w", encoding="utf-8") as file:
            json.dump(habits, file, indent=2, ensure_ascii=False)

    def load_habit_data():
        try:
            with open(FILENAME, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            return []






