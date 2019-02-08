from django.http import HttpResponse
from django_geoserver import settings

def _response_callback(**kwargs):
    affected_layers = kwargs['affected_layers']
    # response = kwargs['response']
    content = kwargs['content']
    status = kwargs['status']
    content_type = kwargs['content_type']

    return HttpResponse(
        content=content,
        status=status,
        content_type=content_type)

def proxy(
        request,
        url=None,
        response_callback=_response_callback,
        sec_chk_hosts=True,
        sec_chk_rules=True,
        **kwargs):


    # TODO: удалить
    res = "HELLO"

    # Security rules and settings
    PROXY_ALLOWED_HOSTS = getattr(settings, 'PROXY_ALLOWED_HOSTS', ())

    # Sanity url checks
    if 'url' not in request.GET and not url:
        return HttpResponse("The proxy service requires a URL-encoded URL as a parameter.",
                            status=400,
                            content_type="text/plain"
                            )

    raw_url = url or request.GET['url']

    res = raw_url
    return HttpResponse(res, status=200)

