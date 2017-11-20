class Period:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

    @staticmethod
    def find(periods, target):
        for period in periods:
            if period.start <= target < period.end:
                return period.name
        return None
