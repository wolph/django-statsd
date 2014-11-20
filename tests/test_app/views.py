from django import http
import time


def index(request, delay=None):
    if delay:
        time.sleep(float(delay))

    return http.HttpResponse('Index page')
