from django.urls import re_path
from . import views

urlpatterns = [
    # REST Endpoints

    # OWS Endpoints
    re_path(
        r'^wms',
        views.geoserver_protected_proxy,
        dict(
            proxy_path='/gs/wms',
            downstream_path='wms',
            workspace='nyc_roads'
        ),
        name='wms_endpoint'),
]