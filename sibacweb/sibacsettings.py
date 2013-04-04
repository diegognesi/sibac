SIBACDATASOURCE = {
    'PROVIDER': 'postgis',       # Strings for built-in providers or module variables for custom providers.
    'DBNAME': 'sibacdb',
    'USER': 'sibacuser',
    'PASSWORD': 'sibacpwd',
    'HOST': 'localhost',
    'PORT': '',
    'FULLTEXT': True,            # True if the data source supports full text searches.
    'FULLTEXT_LANG': 'italian' , # Language used for full text searches.
    'USERS_TABLE': 'auth_user',  # Empty if no user management is required. 'auth_user' if using django + postgres.
    'USERS_ID_FIELD': 'id'       # Empty if no user management is required. 'id' if using django + postgres.
}

# GEOREFERENCING:
#
# EPSGID:
#    Change this value *BEFORE* initializing the storage. It specifies which
#    coordinate system will be used by default. With some providers, it could be
#    the ONLY available coordinate system. You can use QGIS to search for the
#    correct EPSG ID number.
#    Some possible values are:
#      4326: WGS 84 (Defalut)
#      3003: Rome, Monte Mario, Italy, Zone 1 (Gauss-Boaga W)
#      3004: Rome, Monte Mario, Italy, Zone 2 (Gauss-Boaga E)
#

GEOREFERENCING = {
    'EPSGID': 4326,
}
