from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from owslib import wfs
import json
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom
import requests



@csrf_exempt
def wms_endpoint(request):
    if request.GET:
        # check params
        if not request.GET["service"] == "WMS":
            return HttpResponse("bad request", status=404)
        if not request.GET["version"] == "1.1.1":
            return HttpResponse("bad request", status=404)

        if request.GET["request"] == "GetMap":
            res = requests.get("http://geoserver:8080/geoserver/wms", request.GET)
            format = 'image/png' or request.GET["format"]
            return HttpResponse(res, status=res.status_code, content_type=format)
    return HttpResponse("bad request", status=404)


@csrf_exempt
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
                        res = service.getfeature(typename=typename, outputFormat="json", srsname="EPSG:4326")
                        return HttpResponse(res.read(), status="200", content_type="application/json")
                    else:
                        return HttpResponse("layer not found", status=404)
                else:
                    return HttpResponse("typename is required", status=404)

        else:
            res = service.getcapabilities()
            return HttpResponse(res.read(), status=200, content_type="text/xml")
    elif request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        if not data and data["service"] == "WFS" and not data["version"] == "1.1.0":
            return HttpResponse("bad request", status=404)
        else:
            # if Transaction
            if data["request"] == "Transaction":
                # Insert
                if data["transactionType"] == "Insert":
                    transactionRequest = _create_gml_transaction_insert(data)
                    transactionResponse = requests.post("http://geoserver:8080/geoserver/wfs", transactionRequest)
                    return HttpResponse(transactionResponse.content, status=transactionResponse.status_code)

                # Update
                if data["transactionType"] == "Update":
                    # if GEOM
                    if data["layer_attributes"]["coords"]:
                        transactionRequest = _create_gml_transaction_update(data)
                        transactionResponse = requests.post("http://geoserver:8080/geoserver/wfs", transactionRequest)
                        return HttpResponse(transactionResponse.content, content_type='text/xml', status=transactionResponse.status_code)

                # Delete
                if data["transactionType"] == "Delete":
                    # if ID
                    if data["layer_attributes"]["fid"]:
                        transactionRequest = _create_gml_transaction_delete(data)
                        transactionResponse = requests.post("http://geoserver:8080/geoserver/wfs", transactionRequest)
                        return HttpResponse(transactionResponse, content_type='text/xml', status=transactionResponse.status_code)
    else:
        return HttpResponse("bad request", status=404)

    return HttpResponse(res, status=200)


def _prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def _create_gml_transaction_insert(data):
    # NameSpaces
    xmlns_wfs = "http://www.opengis.net/wfs"
    xmlns_gml = "http://www.opengis.net/gml"
    xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
    # TODO: interactive
    xmlns_workspace = "http://www.tcartadata.com/test"
    xsi_schemaLocation = "http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/WFS-transaction.xsd http://www.tcartadata.com/test http://geoserver:8080/geoserver/wfs/DescribeFeatureType?typename=test:drawing"

    ElementTree.register_namespace("wfs", xmlns_wfs)
    ElementTree.register_namespace("xsi", xmlns_xsi)
    ElementTree.register_namespace("gml", xmlns_gml)
    ElementTree.register_namespace("test", xmlns_workspace)

    # XmlDOM
    transaction = Element("{http://www.opengis.net/wfs}Transaction")
    transaction.set("service", data["service"])
    transaction.set("version", data["version"])
    transaction.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", xsi_schemaLocation)
    insert = SubElement(transaction, "{http://www.opengis.net/wfs}Insert")
    drawing = SubElement(insert, "{http://www.tcartadata.com/test}drawing")

    bin = SubElement(drawing, "{http://www.tcartadata.com/test}bin")
    bin.text = data["layer_attributes"]["bin"]

    custom_value = SubElement(drawing, "{http://www.tcartadata.com/test}custom_value")
    custom_value.text = data["layer_attributes"]["custom_value"]

    # The geom
    the_geom = SubElement(drawing, "{http://www.tcartadata.com/test}the_geom")

    # If Polygon
    if data["layer_attributes"]["geometry_type"] == "Polygon":
        polygon = SubElement(the_geom, "{http://www.opengis.net/gml}Polygon")
        polygon.set("srsName", data["layer_attributes"]["crs"])
        polygon.set("srsDimension", "2")

        exterior = SubElement(polygon, "{http://www.opengis.net/gml}exterior")
        LinearRing = SubElement(exterior, "{http://www.opengis.net/gml}LinearRing")
        LinearRing.set("srsDimension", "2")

        posList = SubElement(LinearRing, "{http://www.opengis.net/gml}posList")

        coords = data["layer_attributes"]["coords"]
        res = ""
        for point in coords[0]:
            res += str(point[0]) + " " + str(point[1]) + " "
        posList.text = res

    return _prettify(transaction)


def _create_gml_transaction_update(data):
    # NameSpaces
    xmlns_wfs = "http://www.opengis.net/wfs"
    xmlns_gml = "http://www.opengis.net/gml"
    xmlns_ogc = "http://www.opengis.net/ogc"
    xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
    xmlns_workspace = "http://www.tcartadata.com/test"
    xsi_schemaLocation = "http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd"

    ElementTree.register_namespace("wfs", xmlns_wfs)
    ElementTree.register_namespace("xsi", xmlns_xsi)
    ElementTree.register_namespace("gml", xmlns_gml)
    ElementTree.register_namespace("test", xmlns_workspace)

    # XmlDOM
    transaction = Element("{http://www.opengis.net/wfs}Transaction")

    transaction.set("service", data["service"])
    transaction.set("version", data["version"])
    transaction.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", xsi_schemaLocation)

    update = SubElement(transaction, "{http://www.opengis.net/wfs}Update")
    update.set("typeName", data["typename"])

    Property = SubElement(update, "{http://www.opengis.net/wfs}Property")

    Name = SubElement(Property, "{http://www.opengis.net/wfs}Name")
    Name.text = "the_geom"
    Value = SubElement(Property, "{http://www.opengis.net/wfs}Value")

    # MultiSurface = SubElement(Value, "{http://www.opengis.net/gml}MultiSurface")
    # surfaceMember = SubElement(MultiSurface, "{http://www.opengis.net/gml}surfaceMember")
    Polygon = SubElement(Value, "{http://www.opengis.net/gml}Polygon")
    Polygon.set("srsName", data["layer_attributes"]["crs"])
    Polygon.set("srsDimension", "2")
    exterior = SubElement(Polygon, "{http://www.opengis.net/gml}exterior")
    LinearRing = SubElement(exterior, "{http://www.opengis.net/gml}LinearRing")
    LinearRing.set("srsDimension", "2")
    posList = SubElement(LinearRing, "{http://www.opengis.net/gml}posList")
    coords = data["layer_attributes"]["coords"]
    res = ""
    for point in coords[0]:
        res += str(point[0]) + " " + str(point[1]) + " "
    # res = res[:-1]
    posList.text = res

    # Filter
    Filter = SubElement(update, "{http://www.opengis.net/ogc}Filter")
    FeatureId = SubElement(Filter, "{http://www.opengis.net/ogc}FeatureId")
    FeatureId.set("fid", data["layer_attributes"]["fid"])

    return _prettify(transaction)


def _create_gml_transaction_delete(data):
    # NameSpaces
    xmlns_wfs = "http://www.opengis.net/wfs"
    xmlns_ogc = "http://www.opengis.net/ogc"
    xmlns_cdf = "http://www.opengis.net/cite/data"
    xmlns_workspace = "http://www.tcartadata.com/test"

    ElementTree.register_namespace("wfs", xmlns_wfs)
    ElementTree.register_namespace("ogc", xmlns_ogc)

    # XmlDOM
    transaction = Element("{http://www.opengis.net/wfs}Transaction")
    transaction.set("service", data["service"])
    transaction.set("version", data["version"])

    delete = SubElement(transaction, "{http://www.opengis.net/wfs}Delete")
    delete.set("typeName", data["typename"])

    # Filter
    Filter = SubElement(delete, "{http://www.opengis.net/ogc}Filter")
    FeatureId = SubElement(Filter, "{http://www.opengis.net/ogc}FeatureId")
    FeatureId.set("fid", data["layer_attributes"]["fid"])

    return _prettify(transaction)

# def _describeFeatureType(data):
#     # NameSpaces
#     xmlns_wfs = "http://www.opengis.net/wfs"
#     ElementTree.register_namespace("wfs", xmlns_wfs)
#
#     describeFeatureType = Element("{http://www.opengis.net/wfs}DescribeFeatureType")
#     describeFeatureType.set("service", data["service"])
#     describeFeatureType.set("version", data["version"])
#
#     typeName = SubElement(describeFeatureType, "TypeName")
#     typeName.text = data["typename"]
#
#     return _prettify(describeFeatureType)
#
#
# def _get_namespace_and_fields(response):
#     root = ElementTree.fromstring(response)
#     namespace = root.attrib["targetNamespace"]
#     sequence = root.findall('sequence')
#     fields = []
#     for field in sequence:
#         fields.append(fields)
#     return fields