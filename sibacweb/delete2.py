import sibacmanage
import sibacsettings
from sibaclib.documents import Document
from sibaclib.search import *
from sibaclib.django.webappsettings import *

provider = sibacmanage.get_provider()
dt = provider.inspector.doc_types["SI"]
vres, se = SearchExpression.validate_expression_string(u'SELECT * FROM SI WHERE NCTN = "2"', provider, False)
print "Espressione valida: ", vres.is_valid
print ""
print "Errori:"
for e in vres.errors:
    print e
print "-----------------------------------------"
print unicode(se)
