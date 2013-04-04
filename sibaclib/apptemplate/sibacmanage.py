# This module contains some functions useful to manage a SIBAC app.
# The functions cann be called directly from the command line, i.e.:
#
# python sibacmanage.py createdb myapp
#

import os
import os.path
import sys
import sibacsettings
import sibaclib.utils

def initialize_storage(app_name):
    """
    This method sets up the storage. I.e., if the storage is a database,
    this method creates the tables required to manage the documents.
    """
    docs_provider = get_provider(app_name)
    docs_provider.initialize_storage()
    #docs_provider.initialize_all_doc_types()

def clear_storage(app_name):
    """
    This method completely clears the storage. If the storage is a database,
    then this method will remove all tables.
    """
    docs_provider = get_provider(app_name)
    docs_provider.clear_storage()

def initialize_doc_type(app_name, dt_sid):
    """
    This method creates the storage entities required to manage a specific
    document type.
    """
    docs_provider = get_provider(app_name)
    docs_provider.initialize_doc_type(dt_sid)

def remove_doc_type(app_name, dt_sid):
    """
    This method removes the storage entities required to manage a specific
    document type.
    """
    docs_provider = get_provider(app_name)
    docs_provider.remove_doc_type(dt_sid)

def initialize_all_doc_types(app_name):
    """
    This method creates the storage entities required to manage all the
    document types.
    """
    docs_provider = get_provider(app_name)
    docs_provider.initialize_all_doc_types()

def remove_all_doc_types(app_name):
    """
    This method removes the storage entities required to manage all the
    document types.
    """
    docs_provider = get_provider(app_name)
    docs_provider.remove_all_doc_types()

def get_provider(app_name):
    """
    This method gets an instance of the correct provider for managing a SIBAC
    storage.
    """
    app_path = os.path.join(os.getcwd(), app_name)
    return sibaclib.utils.initialize_provider(sibacsettings, app_path)

def shell(app_name):
    """
    This method opens the interpreter, imports sibacmanage.py and all SIBAC
    modules and creates a variable called provider that points to an
    initialized SIBAC provider for the specified application.
    """
    c_string = "from sibaclib.documents import Document;\
               from sibaclib.documenttypes import *;\
               import sibacmanage;\
               provider = sibacmanage.get_provider('" + app_name + "')"
    os.system('python -i -c "' + c_string + '"')

if __name__ == "__main__":
    cmd_name = sys.argv[1]
    args=sys.argv[2:]
    locals()[cmd_name](*args)
