from django import http
import time


def index(request, delay=None):
    delay = float(request.GET.get('delay', 0))
    if delay:
        time.sleep(float(delay))

    return http.HttpResponse('Index page')
