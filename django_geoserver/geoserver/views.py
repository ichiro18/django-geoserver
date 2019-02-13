from django.http import HttpResponse
from owslib import wfs


def wms_endpoint(request):
    res = "HELLO"
    return HttpResponse(res, status=200)


def wfs_endpoint(request):
    res = "HELLO"
    # TODO: check auth & permissions
    service = wfs.WebFeatureService("http://geoserver:8080/geoserver/wfs", version="1.1.0", username="admin", password="geoserver")
    if request.method == "GET":
        # if request without params
        if request.GET and not request.GET["request"] == "GetCapabilities":
            # check params
            if not request.GET["service"] == "WFS":
                return HttpResponse("bad request", status=404)
            if not request.GET["version"] == "1.1.0":
                return HttpResponse("bad request", status=404)

            # if GetFeature
            if request.GET["request"] == "GetFeature":
                # get layer
                if "typename" in request.GET:
                    typename = request.GET["typename"]
                    contents = service.contents
                    # check typename
                    if typename in list(contents):
                        res = service.getfeature(typename=typename, outputFormat="json")
                        return HttpResponse(res.read(), status="200", content_type="application/json")
                    else:
                        return HttpResponse("layer not found", status=404)
                else:
                    return HttpResponse("typename is required", status=404)

        else:
            res = service.getcapabilities()
            return HttpResponse(res.read(), status=200, content_type="text/xml")
    elif request.method == "POST":
        res = "POST"
    else:
        return HttpResponse("bad request", status=404)
    # feature = service.getfeature(typename="	test:nyc_buildings", outputFormat="json")
    # feature = service.getfeature(typename="test:drawing")

    # res = feature.info
    return HttpResponse(res, status=200)