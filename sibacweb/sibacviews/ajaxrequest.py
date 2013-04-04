from django.http import HttpResponse, Http404
from django.utils import simplejson
import os
from HTMLParser import HTMLParser
import sibaclib.utils
import sibacsettings
from sibaclib.search import SearchExpression

#Initialize sibac provider.
provider = sibaclib.utils.initialize_provider(sibacsettings, os.path.dirname(sibacsettings.__file__))

# TODO: Check user permissions.

def get_dt_paragraphs(request):
    """Returns a list of paragraphs for a specific document type."""
    if request.method == 'GET':
        dt_sid = request.GET["dt_sid"]
        dt = provider.inspector.doc_types[dt_sid]
        paragraphs = [{ "sid": p.sid, "alt": p.alt } for p in dt.paragraphs]
        response = simplejson.dumps({"paragraphs": paragraphs})
        return HttpResponse (response, mimetype='application/json')
    else:
        raise Http404()

def get_dt_fields(request):
    """Returns the list of simple fields and subfields for a specific document_type."""
    if request.method == 'GET':
        dt_sid = request.GET["dt_sid"]
        dt = provider.inspector.doc_types[dt_sid]
        fields = [{"sid": k, "text": v.alt} for k, v in dt.simple_fields.iteritems()] 
        response = simplejson.dumps({"fields": fields})
        return HttpResponse (response, mimetype='application/json')
    else:
        raise Http404()

def validate_search_expression(request):
    """Validates a search expression."""
    if request.method == 'GET':
        expr = request.GET.get("expr", None)
        if not expr:
            return HttpResponse(status=400)
        allow_for_storage_only = request.GET.get('allow_for_storage_only', [])[:1]
        if allow_for_storage_only == "true":
            allow_for_storage_only = True
        else:
            allow_for_storage_only = False
        val_result, se = SearchExpression.validate_expression_string(expr, provider, allow_for_storage_only)
        response_dict = {"is_valid": val_result.is_valid, "errors": val_result.errors}
        if val_result.is_valid:
            response_dict["expr"] = unicode(se)
        return HttpResponse (simplejson.dumps(response_dict), mimetype='application/json')
    else:
        raise Http404()

