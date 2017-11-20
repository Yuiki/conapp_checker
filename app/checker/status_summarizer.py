from collections import OrderedDict

from app.checker.period import Period


class StatusSummarizer:
    def __init__(self, status_fetcher):
        self.fetcher = status_fetcher

    def summarize(self, query, periods):
        summary = OrderedDict([(period.name, 0) for period in periods])
        calc_start = periods[0].start
        for status in self.fetcher.gen_status():
            if status.retweeted:
                continue

            tweet_time = status.created_at
            if tweet_time < calc_start:
                return summary
            if query in status.text:
                summary[Period.find(periods, tweet_time)] += 1
        return summary
