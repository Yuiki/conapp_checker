from collections import OrderedDict
from datetime import datetime, timedelta

import tweepy
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from social_django.models import UserSocialAuth


@login_required
def check(request):
    user = UserSocialAuth.objects.get(user_id=request.user.id)
    oauth_token = user.extra_data['access_token']['oauth_token']
    oauth_token_secret = user.extra_data['access_token']['oauth_token_secret']
    logout(request)
    consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
    consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET
    summary = calc_tweet_summary(consumer_key, consumer_secret, oauth_token, oauth_token_secret)
    return render(request, 'app/check.html', dict(summary=summary))


def calc_tweet_summary(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    hashtag = '#コンテンツ応用論2017'
    date_fmt = '%m/%d'

    lecture_dates = [(10, 2), (10, 10), (10, 16), (10, 23), (10, 30), (11, 13), (11, 20)]
    lecture_date_times = [datetime(2017, date[0], date[1]) for date in lecture_dates]
    summary = OrderedDict([(date.strftime(date_fmt), 0) for date in lecture_date_times])

    max_id = -1

    cont = True
    while cont:
        try:
            statuses = get_user_timeline(api, max_id)
        except tweepy.RateLimitError:
            break
        if not statuses:
            break
        for status in statuses:
            calc_start = lecture_date_times[0] + timedelta(days=1)
            tweet_time = status.created_at
            if tweet_time < calc_start:
                cont = False
            if hashtag in status.text:
                for idx, lecture_date in enumerate(lecture_date_times):
                    # 第一回目は集計対象外
                    if idx == 0:
                        continue
                    previous_lecture_date = lecture_date_times[idx - 1]
                    start = previous_lecture_date + timedelta(days=1)
                    end = lecture_date + timedelta(days=1)
                    if start <= tweet_time < end:
                        summary[lecture_date.strftime(date_fmt)] += 1
        else:
            max_id = statuses[-1].id - 1
    # 第一回は集計対象外
    summary.popitem(last=False)
    return summary


def get_user_timeline(api, max_id):
    count = 200
    if max_id == -1:
        return api.user_timeline(count=count)
    return api.user_timeline(count=count, max_id=max_id)
