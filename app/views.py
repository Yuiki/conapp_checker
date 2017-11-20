from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from social_django.models import UserSocialAuth

from app.checker.summarize_conapp_statuses import summarize_conapp_statuses


@login_required
def check(request):
    user = UserSocialAuth.objects.get(user_id=request.user.id)
    username = user.user.username
    oauth_token = user.extra_data['access_token']['oauth_token']
    oauth_token_secret = user.extra_data['access_token']['oauth_token_secret']
    logout(request)
    consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
    consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET
    summary = summarize_conapp_statuses(consumer_key, consumer_secret, oauth_token, oauth_token_secret)
    return render(request, 'app/check.html', dict(username=username, summary=summary))
