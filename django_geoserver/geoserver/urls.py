from django.urls import re_path
from . import views

urlpatterns = [
    # REST Endpoints

    # OWS Endpoints
    re_path(
        r'^wms',
        views.wms_endpoint,
        name='wms_endpoint'),

    re_path(
        r'^wfs',
        views.wfs_endpoint,
        name='wfs_endpoint'),
]