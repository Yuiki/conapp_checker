from datetime import datetime, timedelta

from app.checker.my_status_fetcher import MyStatusFetcher
from app.checker.period import Period
from app.checker.status_summarizer import StatusSummarizer


def summarize_conapp_statuses(consumer_key, consumer_secret, access_token, access_token_secret):
    status_fetcher = MyStatusFetcher(consumer_key, consumer_secret, access_token, access_token_secret)
    hashtag = '#コンテンツ応用論2017'
    # 第一回は集計対象外
    lecture_dates = [(10, 2), (10, 10), (10, 16), (10, 23), (10, 30), (11, 13), (11, 20), (12, 4)]
    periods = []
    date_fmt = '%m/%d'
    for idx, date in enumerate(lecture_dates):
        lecture_date = datetime(2017, date[0], date[1])
        name = lecture_date.strftime(date_fmt)
        end = lecture_date + timedelta(days=1)
        if idx == 0:
            start = end
        else:
            previous_period = periods[idx - 1]
            start = previous_period.end
        periods.append(Period(name, start, end))
    else:
        del periods[0]

    summarizer = StatusSummarizer(status_fetcher)
    return summarizer.summarize(hashtag, periods)
