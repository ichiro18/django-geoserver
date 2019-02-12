from django.shortcuts import render
# from geoserver.catalog import Catalog
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService

# Create your views here.
def index(request):
    #
    # REST_example
    #
    # cat = Catalog("http://geoserver:8080/geoserver/rest/", username="admin", password="geoserver")
    # workspace = cat.get_workspace("test")
    # resources = cat.get_resources(workspace=workspace)
    # testVar = resources
    #
    # OWS_example
    # wms
    wms = WebMapService("http://geoserver:8080/geoserver/wms")
    wms_services = list(wms.contents)
    # wfs
    wfs = WebMapService("http://geoserver:8080/geoserver/wfs", version="1.1.1", username="admin", password="geoserver")
    wfs_services = list(wfs.contents)
    # result
    testVar = "hello"
    testVar = wfs_services
    return render(request, 'web/index.html', {'testVar' : testVar})