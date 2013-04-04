SIBACDATASOURCE = {
    'PROVIDER': 'postgis',
    'DBNAME': 'sibacdb',
    'USER': 'sibacuser',
    'PASSWORD': 'sibacpwd',
    'HOST': 'localhost',
    'PORT': '',
    'FULLTEXT': True,                # True if the data source supports full text searches.
    'FULLTEXT_LANG': 'italian'       # Language used for full text searches.
}

# GEOREFERENCING:
#
# EPSGID:
#    Change this value *BEFORE* initializing the storage. It specifies which
#    coordinate system will be used by default. With some providers, it could be
#    the ONLY available coordinate system. You can use QGIS to search for the
#    correct EPSG ID number.
#    Some values are:
#      4326: WGS 84 (Defalut)
#      3003: Rome, Monte Mario, Italy, Zone 1 (Gauss-Boaga W)
#      3004: Rome, Monte Mario, Italy, Zone 2 (Gauss-Boaga E)
#

GEOREFERENCING = {
    'EPSGID': 4326,
}
