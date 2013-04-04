import os
from sibaclib.django.webappsettings import ApplicationPermissions, DocumentPermissions, EmailSettings, WebAppSettings
import sibaclib.utils
import sibacsettings
#try:
#   import cPickle as pickle
#except:
import pickle

app_path = os.path.join(os.getcwd(), "sibacapp")
provider = sibaclib.utils.initialize_provider(sibacsettings, os.path.dirname(sibacsettings.__file__))

def sibac_settings(request):
    """ Add a Web_App_Settings variable to the texmplate context.

    The variable will point to a WebAppSettings instance.
    Settings are stored in a database. If no settings are found in the db,
    this method will instantiate a new WebAppSettings object with default
    attribute values.
    """
    sett_serialized = provider.get_setting("_WebAppSettings")
    if sett_serialized:
        wapp_settings = WebAppSettings.from_json(sett_serialized)
    else:
        wapp_settings = WebAppSettings()
        wapp_settings.title = "SIBAC 1.0"
        wapp_settings.subtitle = "Sistema Informativo per i Beni Ambientali e Culturali"
        wapp_settings.url = None
        wapp_settings.description = "Sistema Informativo Open Source per la gestione e la consultazione di schede di catalogo."
        wapp_settings.keywords = "SIBAC ICCD Beni culturali e ambientali catalogazione"
        wapp_settings.copyright = "Nota di copyright. Modifica questa nota dalla sezione Impostazioni."
    doc_permissions = wapp_settings.app_permissions.permissions
    # Remove permissions referring to documents that don't exist anymore
    for p in doc_permissions.keys():
        if not p in provider.inspector.doc_types:
            del doc_permissions[p]
    # Add default permissions for documents that don't exists in the
    # permission dictionary
    for dt in provider.inspector.doc_types:
        if not dt in doc_permissions:
            doc_permissions[dt] = DocumentPermissions(dt_sid=dt)
    return { "WebAppSettings": wapp_settings }
