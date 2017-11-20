from collections import OrderedDict
from datetime import datetime, timedelta

import tweepy
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from social_django.models import UserSocialAuth

DATE_FMT = '%m/%d'


@login_required
def check(request):
    user = UserSocialAuth.objects.get(user_id=request.user.id)
    oauth_token = user.extra_data['access_token']['oauth_token']
    oauth_token_secret = user.extra_data['access_token']['oauth_token_secret']
    logout(request)
    consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
    consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET
    summary = summarize_conapp_statuses(consumer_key, consumer_secret, oauth_token, oauth_token_secret)
    return render(request, 'app/check.html', dict(summary=summary))


def summarize_conapp_statuses(consumer_key, consumer_secret, access_token, access_token_secret):
    status_fetcher = MyStatusFetcher(consumer_key, consumer_secret, access_token, access_token_secret)
    hashtag = '#コンテンツ応用論2017'
    # 第一回は集計対象外
    lecture_dates = [(10, 2), (10, 10), (10, 16), (10, 23), (10, 30), (11, 13), (11, 20)]
    periods = []
    for idx, date in enumerate(lecture_dates):
        lecture_date = datetime(2017, date[0], date[1])
        name = lecture_date.strftime(DATE_FMT)
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


class MyStatusFetcher:
    COUNT = 200

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def gen_status(self):
        max_id = None
        while True:
            try:
                if not max_id:
                    statuses = self.api.user_timeline(count=self.COUNT)
                else:
                    statuses = self.api.user_timeline(count=self.COUNT, max_id=max_id)
            except tweepy.RateLimitError:
                return
            if statuses:
                for status in reversed(statuses):
                    if not status.retweeted:
                        max_id = status.id - 1
                        break
            else:
                return
            for status in statuses:
                yield status
