from django.http import HttpResponse


def wms_endpoint(request):
    res = "HELLO"
    return HttpResponse(res, status=200)