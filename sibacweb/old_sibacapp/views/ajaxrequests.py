from django.http import HttpResponse, Http404
from django.utils import simplejson
import os
import sibaclib.utils
import sibacsettings

#try:
#   import cPickle as pickle
#except:
import pickle

#Initialize sibac provider.
provider = sibaclib.utils.initialize_provider(sibacsettings, "/home/diego/djcode/sibacweb/sibacapp")

# TODO: Check user permissions.

def get_dt_paragraphs(request):
    """Returns a list of paragraphs for a specific document type."""
    if request.method == 'GET':
        dt_sid = request.GET["dt_sid"]
        dt = provider.inspector.doc_types[dt_sid]
        paragraphs = [p.sid for p in dt.paragraphs]
        response = simplejson.dumps({"paragraphs": paragraphs})
        print __path__
        return HttpResponse (response, mimetype='application/json')
    else:
        raise Http404()
