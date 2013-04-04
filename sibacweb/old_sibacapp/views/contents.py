from django.shortcuts import render
import os
import sibaclib.utils
import sibacsettings
from django.http import HttpResponse, Http404

#Initialize sibac provider.
provider = sibaclib.utils.initialize_provider(sibacsettings, os.getcwd())

def serve_static_content(key, request):
    if request.method == 'GET':
        content = provider.get_setting(key)
        return render(request, 'static_content.html', { "page_content": content })
    elif request.method == 'POST':
        page_content = request.POST["page_content"]
        provider.change_setting(key, page_content)
        return HttpResponse()
    else:
        raise Http404()

def home(request):
    return serve_static_content("_StaticContentHome", request)

def about(request):
    return serve_static_content("_StaticContentAbout", request)

def links(request):
    return serve_static_content("_StaticContentLinks", request)

def contacts(request):
    return serve_static_content("_StaticContentContacts", request)
