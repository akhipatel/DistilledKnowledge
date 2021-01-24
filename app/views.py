# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template


from collections import OrderedDict

from fusioncharts import FusionCharts


@login_required(login_url="/login/")
def index(request):
    return render(request, "index.html")

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'error-404.html' )
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        
        print(e)
        html_template = loader.get_template( 'error-500.html' )
        return HttpResponse(html_template.render(context, request))

   
    
def map(request):

    # Chart data is passed to the `dataSource` parameter, as dict, in the form of key - value pairs.
    dataSource = OrderedDict()

    # The `mapConfig` dict contains key - value pairs data for chart attribute
    mapConfig = OrderedDict()
    mapConfig["caption"] = "Average Annual Population Growth"
    mapConfig["subcaption"] = "1955-2015"
    mapConfig["numbersuffix"] = "%"
    mapConfig["includevalueinlabels"] = "1"
    mapConfig["labelsepchar"] = ":"
    mapConfig["entityFillHoverColor"] = "#FFF9C4"
    mapConfig["theme"] = "fusion"

    # Map color range data
    colorDataObj = {
        "minvalue": "0",
        "code": "#FFE0B2",
        "gradient": "1",
        "color": [{
                "minValue": "0.5",
                "maxValue": "1",
                "code": "#FFD74D"
            },
            {
                "minValue": "1.0",
                "maxValue": "2.0",
                "code": "#FB8C00"
            },
            {
                "minValue": "2.0",
                "maxValue": "3.0",
                "code": "#E65100"
            }
        ]
    }

    dataSource["chart"] = mapConfig
    dataSource["colorrange"] = colorDataObj
    dataSource["data"] = []


    # Map data array
    mapDataArray = [
        ["NA", "0.82", "1"],
        ["SA", "2.04", "1"],
        ["AS", "1.78", "1"],
        ["EU", "0.40", "1"],
        ["AF", "2.58", "1"],
        ["AU", "1.30", "1"]
    ]


    # Iterate through the data in `mapDataArray` and insert in to the `dataSource["data"]` list.
    #The data for the `data` should be in an array wherein each element 
    #of the array is a JSON object# having the `id`, `value` and `showlabel` as keys.
    for i in range(len(mapDataArray)):
        dataSource["data"].append({
            "id": mapDataArray[i][0],
            "value": mapDataArray[i][1],
            "showLabel": mapDataArray[i][2]
        })

# Create an object for the world map using the FusionCharts class constructor
# The chart data is passed to the `dataSource` parameter.
    usionMap = FusionCharts("maps/world", "myFirstMap", "650", "450", "myFirstmap-container", "json", dataSource)

# returning complete JavaScript and HTML code, which is used to generate map in the browsers.
    return render(request, 'index.html', {'output': fusionMap.render()})
