class WorkdaysFromSeconds(object):
    def __init__(self, seconds):
        self.seconds = seconds
        self._hours = seconds // (60.0 * 60)
        self._days, self._day_hours = divmod(self._hours, 8)

    def __sub__(self, other):
        return WorkdaysFromSeconds(self.seconds - other.seconds)

    def __add__(self, other):
        return WorkdaysFromSeconds(self.seconds + other.seconds)

    @property
    def days(self):
        return self._days

    @property
    def day_hours(self):
        return self._day_hours

    @property
    def hours(self):
        return self._hours

    def __repr__(self):
        return "%dd %.2fh (%.2fh)" % (self._days, self._day_hours, self._hours)
