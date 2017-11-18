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

    lecture_dates = [(10, 2), (10, 10), (10, 16), (10, 23), (10, 30), (11, 13)]
    lecture_start_times = [datetime(2017, date[0], date[1]) for date in lecture_dates]
    summary = {date.strftime(date_fmt): 0 for date in lecture_start_times}

    max_id = api.user_timeline(count=1)[0].id

    cont = True
    while cont:
        try:
            statuses = api.user_timeline(count=200, max_id=max_id)
        except tweepy.RateLimitError:
            break
        if not statuses:
            break
        for status in statuses:
            max_id = status.id - 1
            first_lecture_date = lecture_start_times[0]
            tweet_time = status.created_at
            if tweet_time < first_lecture_date:
                cont = False
            if hashtag in status.text:
                for idx, lecture_start_time in enumerate(lecture_start_times):
                    if idx == 0:
                        continue
                    previous_lecture_start_time = lecture_start_times[idx - 1]
                    if previous_lecture_start_time + timedelta(days=1) <= tweet_time < lecture_start_time + timedelta(days=1):
                        summary[lecture_start_time.strftime(date_fmt)] += 1
    del summary[lecture_start_times[0].strftime(date_fmt)]
    return summary
