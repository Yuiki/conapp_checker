from django.shortcuts import redirect
from social_django.middleware import SocialAuthExceptionMiddleware


# HACK
class CustomSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        return redirect('/')
