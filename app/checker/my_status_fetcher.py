import tweepy


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
