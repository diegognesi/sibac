import sibacmanage
from sibaclib.documents import Document
from sibaclib.search import *

p = sibacmanage.get_provider("sibacapp")
d = Document()
d.provider = p
d.dt_sid = "SI"
d.content = [
              ["CD", [
                       ["TSK", "SI"],
                       ["LIR", "I"],
                       ["NCT", [
                                 ["NCTR", "11"],
                                 ["NCTN", "00000001"],
                                 ["NCTS", "a"]
                               ]
                       ],
                       ["NCT", [
                                 ["NCTR", "11"],
                                 ["NCTN", "00000002"],
                                 ["NCTS", "a"]
                               ]
                       ],
                       ["ECP", "S01"],
                       ["ECS", "Pippo"],
                       ["ECS", "Pluto"]
                     ]
              ],
              ["RV", "Relazioni"],
              ["CD", [
                       ["TSK", "SI"],
                       ["LIR", "I"],
                       ["NCT", [
                                 ["NCTR", "11"],
                                 ["NCTN", "00000003"],
                                 ["NCTS", "a"]
                               ]
                       ],
                       ["NCT", [
                                 ["NCTR", "11"],
                                 ["NCTN", "00000004"],
                                 ["NCTS", "a"]
                               ]
                       ],
                       ["ECP", "S01"],
                       ["ECS", "Pippo"],
                       ["ECS", "Pluto"],
                     ]
              ],
            ]
#r = d.validate()
#print "Can be saved:", r.can_be_saved
#print "Cat level:", r.catalogation_level
#for v in r.validation_errors:
#   print "ERROR!"
#   print "error:", v.error_type
#   print "message:", v.error_message
#se = SearchExpression('SELECT * FROM SI WHERE [SI.CD.NCT.NCTN._as_value]>"0" AND [SI.CD.ECP] LIKE "s"')
#res = d.validate_against_expr(se)
#print res

print d.get_contents("NCTN")
