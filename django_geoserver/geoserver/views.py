import re
from django.views.decorators.csrf import csrf_exempt
from django_geoserver import settings
from urllib.parse import urljoin, urlsplit
from .helpers import proxy

# Create your views here.


@csrf_exempt
def geoserver_protected_proxy(
        request,
        proxy_path,
        downstream_path,
        workspace=None,
        layername=None):
    return geoserver_proxy(
        request,
        proxy_path,
        downstream_path,
        workspace=workspace,
        layername=layername
    )


@csrf_exempt
def geoserver_proxy(
        request,
        proxy_path,
        downstream_path,
        workspace=None,
        layername=None):

    # auth
    # if not request.user.is_authenticated:
    #     return HttpResponse(
    #         "You must be logged in to access GeoServer",
    #         content_type="text/plain",
    #         status=401
    #     )

    def strip_prefix(path, prefix):
        assert path.startswith(prefix)
        full_prefix = "%s/%s/%s" % (
            prefix, layername, downstream_path) if layername else prefix
        return path[len(full_prefix):]

    path = strip_prefix(request.get_full_path(), proxy_path)

    raw_url = str(
        "".join([settings.GEOSERVER_CONFIG['LOCATION'], downstream_path, path])
    )

    if settings.DEFAULT_WORKSPACE or workspace:
        ws = (workspace or settings.DEFAULT_WORKSPACE)
        if ws and ws in path:
            # Strip out WS from PATH
            try:
                path = "/%s" % strip_prefix(path, "/%s:" % (ws))
            except BaseException:
                pass

        if proxy_path == '/gs/%s' % settings.DEFAULT_WORKSPACE and layername:
            import posixpath
            raw_url = urljoin(settings.GEOSERVER_CONFIG['LOCATION'],
                              posixpath.join(workspace, layername, downstream_path, path))
            res = raw_url

        if downstream_path in ('rest/styles') and len(request.body) > 0:
            if ws:
                # Lets try
                # http://localhost:8080/geoserver/rest/workspaces/<ws>/styles/<style>.xml
                _url = str("".join([settings.GEOSERVER_CONFIG['LOCATION'],
                                    'rest/workspaces/', ws, '/styles',
                                    path]))
            else:
                _url = str("".join([settings.GEOSERVER_CONFIG['LOCATION'],
                                    'rest/styles',
                                    path]))
            raw_url = _url

    if downstream_path in 'ows' and (
            'rest' in path or
            re.match(r'/(w.*s).*$', path, re.IGNORECASE) or
            re.match(r'/(ows).*$', path, re.IGNORECASE)):
        _url = str("".join([settings.GEOSERVER_CONFIG['LOCATION'], '', path[1:]]))
        raw_url = _url

    url = urlsplit(raw_url)

    affected_layers = None
    if request.method in ("POST", "PUT"):
        # TODO add worker
        pass
    kwargs = {'affected_layers': affected_layers}

    return proxy(request, url=raw_url, **kwargs)
