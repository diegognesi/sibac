import os.path
import importlib
from dtinspector import DocumentTypesInspector
import distutils.dir_util

def create_sibac_app(target_folder=os.getcwd()):
    """Creates a SIBAC application in the specified folder.

    Usage samples:

    createsibacapp(target_folder="/home/diego/apps/sibac/")
    
    createsibacapp()

    When the target_folder argument is not specified, the current working directory will
    be used as target.

    app_name is the name of the directory containing the application.
    The default value is "sibacapp".
    """
    module_dir = os.path.dirname(__file__)
    template_dir = os.path.join(module_dir, "apptemplate")
    distutils.dir_util.copy_tree(template_dir, target_folder)

    print "SIBAC Application successfully created."

def initialize_provider(settings, app_path):
    inspector = DocumentTypesInspector(os.path.join(app_path, "sibacmodels"))
    provider_name = settings.SIBACDATASOURCE['PROVIDER']
    if isinstance(provider_name, basestring):
        # String are used for built-in providers.
        prov_module = importlib.import_module("sibaclib.providers." + provider_name)
    else:
        # Modules references are used for custom providers.
        prov_module = provider_name
    return prov_module.SibacProvider(settings, app_path, inspector)
