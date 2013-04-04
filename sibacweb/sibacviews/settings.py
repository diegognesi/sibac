# -*- coding: utf-8 -*-
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from sibaclib.django.webappsettings import WebAppSettings
import os
import sibaclib.utils
import sibacsettings

#try:
#   import cPickle as pickle
#except:
import pickle

#Initialize sibac provider.
provider = sibaclib.utils.initialize_provider(sibacsettings, os.path.dirname(sibacsettings.__file__))

@login_required
def settings(request):
    if request.method == 'GET':
        return render(request, 'settings.html', {})
    elif request.method == 'POST' and request.is_ajax():
        json_str = request.POST["json_data"]
        # Passing thru object deserialization prevents from
        # inconsistent json.
        app_settings = WebAppSettings.from_json(json_str)
        provider.change_setting("_WebAppSettings", app_settings.to_json())
        return HttpResponse()
    else:
        raise Http404()
