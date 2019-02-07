from django.shortcuts import render
from geoserver.catalog import Catalog
import requests

# Create your views here.
def index(request):
    print("----------------")
    cat = Catalog("http://geoserver:8080/geoserver/rest/", username="admin", password="geoserver")
    req = cat.get_layers()
    # WORKED!!!
    # req = requests.get("http://geoserver:8080/geoserver/rest/about/version")
    # session = requests.Session()
    # req = session.get("http://geoserver:8080/geoserver/rest/about/version")
    # print(all_layers)
    testVar = "hello"
    return render(request, 'index.html', {'testVar' : req[0].name})