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
from bs4 import BeautifulSoup
import requests

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

    except:
    
        html_template = loader.get_template( 'error-500.html' )
        return HttpResponse(html_template.render(context, request))

def get_countries(request):
    req_country = request.POST.get('country').lower()
    page = requests.get('https://epi.yale.edu/epi-indicator-report/H2O')
    content = page.content
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find_all('tr', class_="epi-row-territory H2O")
    length = len(table)
    country_result = {"country": '', "rank": '',"score": '', "error": ''}
    if length > 0:
        for i in range(0, length):
            country = table[i].find('a').getText().lower()
            if req_country == country:
                rank = table[i].find('td', class_="views-field views-field-field-epi-rank-new views-align-right").getText().split()[0]
                score = table[i].find('td', class_="views-field views-field-field-epi-score-new views-align-right").getText().split()[0]
                country_result["country"] = country
                country_result["rank"] = rank
                country_result["score"] = score
            else:
                country_result["error"] = 'Sorry! Not Found'

    html_template = loader.get_template('index.html')
    return render(request, 'index.html', 
    {
        'country': country_result["country"], 
        'rank': country_result["rank"], 
        'score': country_result["score"], 
        'error': country_result["error"]
    })
    