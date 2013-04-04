import os, distutils.dir_util

def create_sibac_app(parent_dir=os.getcwd(), app_name="sibacapp"):
    """
    Creates a SIBAC application, and copies in the parent folder the
    file sibacmanage.py.

    Usage samples:

    createsibacapp(parent_dir="/home/diego/apps/sibac/", app_name="myapp")
    
    createsibacapp()

    When the parent_dir argument is not specified, the current working directory will
    be used as target.

    app_name is the name of the directory containing the application.
    The default value is "sibacapp".
    """
    module_dir = os.path.dirname(__file__)
    apptemplate_dir = os.path.join(module_dir, "apptemplate")
    source_parent_dir = os.path.join(apptemplate_dir, "parent")
    source_app_dir = os.path.join(apptemplate_dir, "app")
    app_dir = os.path.join(parent_dir, app_name)
    distutils.dir_util.copy_tree(source_parent_dir, parent_dir)
    distutils.dir_util.copy_tree(source_app_dir, app_dir)

    print "SIBAC Application successfully created."
