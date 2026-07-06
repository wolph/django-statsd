from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Index page")


def db_query(request: HttpRequest) -> HttpResponse:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return HttpResponse("Query done")


def error(request: HttpRequest) -> HttpResponse:
    raise ValueError("Intentional test error")


def template(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(request, "example.html", {"name": "statsd"})
